import configparser
import csv
import io
import json
import logging
import os
import pathlib
import re
import sys
import warnings
from abc import ABC, abstractmethod
from time import time_ns
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NamedTuple, Optional, TextIO, Tuple, Type, Union

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory, History
from pygments.styles import get_all_styles

from pyocient.api import Connection, SQLException, TypeCodes, connect, custom_type_to_json
from pyocient.api import Warning as OcientWarning
from pyocient.pkg_version import __version__ as version

CONNECT_COMMAND_PATTERN = re.compile(r"^(connect .* using )[^;]+;(.*)$", re.IGNORECASE)
DEFAULT_FETCH_SIZE = 30000

warnings.filterwarnings("always", category=OcientWarning)


# Configuration Management
class PyocientConfig:
    """Manages configuration from both config files and command-line arguments."""

    DEFAULT_CONFIG_FILE = pathlib.Path.home() / ".pyocient"
    DEFAULT_HISTORY_FILE = pathlib.Path.home() / ".pyocient_history"

    # Configuration keys that should be treated as booleans
    BOOLEAN_KEYS = {"nocolor", "nohistory", "echo", "uuid", "version", "time", "noout", "stop_on_error"}

    # Configuration keys that should be treated as integers
    INTEGER_KEYS = {"rows"}

    def __init__(self, config_file: Optional[str] = None, use_config: bool = True):
        """Initialize configuration manager.

        Args:
            config_file: Path to configuration file, or None to disable config file
            use_config: Whether to use configuration file at all
        """
        self.config_file = config_file if config_file else str(self.DEFAULT_CONFIG_FILE)
        self.use_config = use_config and config_file is not None
        self._config_defaults: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if not self.use_config or not os.path.exists(self.config_file):
            return

        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)

            # Flatten all sections into one dict (favor DEFAULT)
            if "DEFAULT" in config:
                self._config_defaults = dict(config["DEFAULT"])

            for section in config.sections():
                self._config_defaults.update(dict(config[section]))

            # Convert types for known configuration keys
            self._convert_types()

        except Exception as e:
            # Log error but don't fail - just use empty defaults
            logging.warning(f"Error loading config file {self.config_file}: {e}")

    def _convert_types(self) -> None:
        """Convert string values to appropriate types."""
        # Convert boolean values
        for key in self.BOOLEAN_KEYS:
            if key in self._config_defaults:
                val = str(self._config_defaults[key]).lower()
                self._config_defaults[key] = val in ("1", "true", "yes", "on")

        # Convert integer values
        for key in self.INTEGER_KEYS:
            if key in self._config_defaults:
                try:
                    self._config_defaults[key] = int(self._config_defaults[key])
                except (ValueError, TypeError):
                    # Keep original value if conversion fails
                    pass

    def get_defaults(self) -> Dict[str, Any]:
        """Get configuration defaults for argparse."""
        return self._config_defaults.copy()

    @classmethod
    def parse_early_args(cls, argv: List[str]) -> Tuple[Optional[str], bool]:
        """Parse --configfile and --noconfig from command line arguments early.

        Returns:
            Tuple of (config_file_path, use_config_flag)
        """
        config_file: Optional[str] = str(cls.DEFAULT_CONFIG_FILE)
        use_config = True

        for i, arg in enumerate(argv):
            if arg == "--noconfig":
                use_config = False
                config_file = None
            elif arg in ("-c", "--configfile") and i + 1 < len(argv):
                config_file = argv[i + 1]

        return (config_file, use_config)


# Command Handler Types and Classes
class CommandResult(NamedTuple):
    """Result of executing a command."""

    connection: Optional[Connection]
    return_code: int


class CommandHandler(ABC):
    """Abstract base class for CLI command handlers."""

    @abstractmethod
    def can_handle(self, tokens: List[str]) -> bool:
        """Check if this handler can process the given tokens."""
        pass

    @abstractmethod
    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        """Handle the command and return the result."""
        pass

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the command name for help documentation."""
        pass

    @abstractmethod
    def get_command_help(self) -> str:
        """Return detailed help text for this command."""
        pass

    def _unquote(self, input_str: str) -> str:
        """Unquote a string, with either single or double quotes."""
        if input_str[0] == '"' and input_str[-1] == '"':
            return input_str[1:-1]
        if input_str[0] == "'" and input_str[-1] == "'":
            return input_str[1:-1]
        return input_str


def _strip_shebang(text: str) -> str:
    """Strip shebang line from text if present.

    Removes the first line if it starts with '#!' to support executable SQL files.
    """
    if text.startswith("#!"):
        # Find the first newline and remove everything up to and including it
        newline_pos = text.find("\n")
        if newline_pos != -1:
            return text[newline_pos + 1 :]
        else:
            # If no newline found, the entire text is just the shebang line
            return ""
    return text


class ConnectHandler(CommandHandler):
    """Handler for CONNECT TO commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        if len(tokens) < 2 or tokens[0].lower() != "connect":
            return False

        # Support both "connect to ..." and "connect to user ..." patterns
        if tokens[1].lower() == "to":
            return True

        return False

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        try:
            # Pattern 1 & 2: connect to <dsn|database> user <username> using <password>
            if len(tokens) == 7 and tokens[3].lower() == "user" and tokens[5].lower() == "using":
                param = self._unquote(tokens[2])
                user = self._unquote(tokens[4])
                password = self._unquote(tokens[6])

                # Check if this looks like a full DSN (contains ://)
                if "://" in param:
                    # Pattern 1: Full DSN connection
                    new_connection = connect(param, user=user, password=password, configfile=args.configfile)
                    return CommandResult(new_connection, os.EX_OK)
                else:
                    # Pattern 2: Database name - need existing connection for host/port
                    if not connection:
                        print("No existing connection to derive host/port from", file=sys.stderr)
                        return CommandResult(connection, os.EX_DATAERR)

                    database = param
                    # Create new connection using existing connection's host/port
                    host_port = f"{connection.hosts[0]}:{connection.port}"
                    new_connection = connect(
                        host=host_port, user=user, password=password, database=database, configfile=args.configfile
                    )
                    return CommandResult(new_connection, os.EX_OK)

            # Pattern 3: connect to user <username> using <password>
            # (same database, different credentials)
            elif len(tokens) == 6 and tokens[2].lower() == "user" and tokens[4].lower() == "using":
                if not connection:
                    print("No existing connection to derive database/host/port from", file=sys.stderr)
                    return CommandResult(connection, os.EX_DATAERR)

                user = self._unquote(tokens[3])
                password = self._unquote(tokens[5])

                # Create new connection using existing connection's host/port/database
                host_port = f"{connection.hosts[0]}:{connection.port}"
                new_connection = connect(
                    host=host_port,
                    user=user,
                    password=password,
                    database=connection.database,
                    configfile=args.configfile,
                )
                return CommandResult(new_connection, os.EX_OK)

            # Pattern 4: connect to <database>
            # (different database, same credentials via security token)
            elif len(tokens) == 3:
                param = self._unquote(tokens[2])

                # Check if this looks like a full DSN (contains ://)
                if "://" in param:
                    # Traditional DSN connection
                    new_connection = connect(param, configfile=args.configfile)
                    return CommandResult(new_connection, os.EX_OK)
                else:
                    # Database name - need existing connection for credentials
                    if not connection:
                        print("No existing connection to derive credentials from", file=sys.stderr)
                        return CommandResult(connection, os.EX_DATAERR)

                    database = param
                    host_port = f"{connection.hosts[0]}:{connection.port}"

                    # Use security token from existing connection
                    new_connection = connect(
                        host=host_port,
                        security_token=connection.security_token,
                        database=database,
                        configfile=args.configfile,
                    )
                    return CommandResult(new_connection, os.EX_OK)

            # Invalid pattern
            print(
                f"Invalid CONNECT TO statement. Usage: connect to <dsn|database> [user <username> using <password>]",
                file=sys.stderr,
            )
            return CommandResult(connection, os.EX_USAGE)

        except SQLException as e:
            print(e, file=sys.stderr)
            return CommandResult(connection, os.EX_OSERR)
        except IOError as exc:
            print(f"I/O Error: {exc}", file=sys.stderr)
            return CommandResult(connection, os.EX_IOERR)
        except ValueError as e:
            print(f"Invalid statement: {e}", file=sys.stderr)
            return CommandResult(connection, os.EX_IOERR)
        except AttributeError as e:
            print(f"Connection error: {e}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "connect"

    def get_command_help(self) -> str:
        return """Connect to an Ocient database.

Usage:
  connect to <dsn>                                    # Full DSN connection
  connect to <dsn> user <username> using <password>   # DSN with explicit credentials
  connect to <database>                               # Switch database (same credentials)
  connect to <database> user <username> using <password>  # Switch database with new credentials
  connect to user <username> using <password>         # Same database, new credentials

Parameters:
  dsn      Data source name or connection string
  database Database name (requires existing connection)
  username Username for authentication
  password Password for authentication

Examples:
  connect to "ocient://localhost:4050/mydb"
  connect to "ocient://server:4050/mydb" user "admin" using "password123"
  connect to "newdb"                                  # Switch to newdb with same credentials
  connect to "newdb" user "admin" using "pass123"     # Switch to newdb with new credentials
  connect to user "newuser" using "newpass"           # Same database, different user

Notes:
  - Database switching requires an existing connection for host/port/credentials
  - Security tokens are preserved when switching databases without explicit credentials
  - Full DSN format: ocient://[username[:password]@]host[:port]/database[?options]"""


class QuitHandler(CommandHandler):
    """Handler for QUIT commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 0 and tokens[0].lower() == "quit"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        if connection:
            connection.close()
        raise EOFError()

    def get_command_name(self) -> str:
        return "quit"

    def get_command_help(self) -> str:
        return """Exit the CLI client.

Usage:
  quit

This command closes the current database connection (if any) and exits the client."""


class SetFormatHandler(CommandHandler):
    """Handler for SET FORMAT commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "format"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        new_format = tokens[2].lower()
        if new_format in ["json", "table", "csv"]:
            args.format = new_format
            print("OK", file=args.outfile)
            return CommandResult(connection, os.EX_OK)
        else:
            print(f"Invalid output format {new_format}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "set format"

    def get_command_help(self) -> str:
        return """Set the output format for query results.

Usage:
  set format <format>

Supported formats:
  json   JSON format
  table  Table format (default)
  csv    CSV format

Examples:
  set format json
  set format table
  set format csv"""


class SetEchoHandler(CommandHandler):
    """Handler for SET ECHO commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "echo"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        echo_val = tokens[2].lower()
        if echo_val in ["on", "true", "1"]:
            args.echo = True
            return CommandResult(connection, os.EX_OK)
        elif echo_val in ["off", "false", "0"]:
            args.echo = False
            return CommandResult(connection, os.EX_OK)
        else:
            print("Invalid echo statement", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "set echo"

    def get_command_help(self) -> str:
        return """Enable or disable command echoing.

Usage:
  set echo <value>

Values:
  on, true, 1   Enable echo
  off, false, 0 Disable echo

Examples:
  set echo on
  set echo off

When echo is enabled, commands are printed before execution."""


class SetTimeHandler(CommandHandler):
    """Handler for SET TIMING commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "timing"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        timing_val = tokens[2].lower()
        if timing_val in ["on", "true", "1"]:
            args.time = True
            return CommandResult(connection, os.EX_OK)
        elif timing_val in ["off", "false", "0"]:
            args.time = False
            return CommandResult(connection, os.EX_OK)
        else:
            print("Invalid timing statement", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "set timing"

    def get_command_help(self) -> str:
        return """Enable or disable command timing.

Usage:
  set timing <value>

Values:
  on, true, 1   Enable echo
  off, false, 0 Disable echo

Examples:
  set timing on
  set timing off

When timing is enabled, the time to execute a command is displayed."""


class SetStopOnErrorHandler(CommandHandler):
    """Handler for SET STOP_ON_ERROR commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "stop_on_error"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        stop_on_error_val = tokens[2].lower()
        if stop_on_error_val in ["on", "true", "1"]:
            args.stop_on_error = True
            return CommandResult(connection, os.EX_OK)
        elif stop_on_error_val in ["off", "false", "0"]:
            args.stop_on_error = False
            return CommandResult(connection, os.EX_OK)
        else:
            print("Invalid stop_on_error statement", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "set stop_on_error"

    def get_command_help(self) -> str:
        return """Enable or disable stopping on errors during file processing.

Usage:
  set stop_on_error <value>

Values:
  on, true, 1   Stop processing on first error
  off, false, 0 Continue processing despite errors

Examples:
  set stop_on_error on
  set stop_on_error off

When stop_on_error is enabled, file processing will halt on the first error.
In interactive mode, this setting has no effect."""


class SetPrintUuidHandler(CommandHandler):
    """Handler for SET PRINTUUID commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "printuuid"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        uuid_val = tokens[2].lower()
        if uuid_val in ["on", "true", "1"]:
            args.uuid = True
            return CommandResult(connection, os.EX_OK)
        elif uuid_val in ["off", "false", "0"]:
            args.uuid = False
            return CommandResult(connection, os.EX_OK)
        else:
            print("Invalid printuuid statement", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "set printuuid"

    def get_command_help(self) -> str:
        return """Enable or disable UUID printing in output.

Usage:
  set printuuid <value>

Values:
  on, true, 1   Enable UUID printing
  off, false, 0 Disable UUID printing

Examples:
  set printuuid on
  set printuuid off"""


class SetRowsHandler(CommandHandler):
    """Handler for SET ROWS commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "rows"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        try:
            args.rows = int(tokens[2])
        except ValueError:
            print(f"Invalid rows value: {tokens[2]}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)
        return CommandResult(connection, os.EX_OK)

    def get_command_name(self) -> str:
        return "set rows"

    def get_command_help(self) -> str:
        return """Set the number of rows to fetch at a time.

Usage:
  set rows <number>

Parameters:
  number  Number of rows to fetch (positive integer)

Examples:
  set rows 100
  set rows 1000

This controls how many rows are fetched from the server in each batch."""


class SetStyleHandler(CommandHandler):
    """Handler for SET STYLE commands."""

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "style"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        # Handle both quoted and unquoted style names
        if len(tokens) < 3:
            print("Usage: set style <style_name>", file=sys.stderr)
            return CommandResult(connection, os.EX_USAGE)

        # Extract style name - handle quoted strings
        new_style = self._unquote(tokens[2])

        # Validate that the style exists
        try:
            available_styles = list(get_all_styles())
            if new_style not in available_styles:
                print(f"Invalid style '{new_style}'. Use 'list styles' to see available styles.", file=sys.stderr)
                return CommandResult(connection, os.EX_DATAERR)

            # Set the style
            args.style = new_style
            print("OK", file=args.outfile)
            return CommandResult(connection, os.EX_OK)

        except Exception as e:
            print(f"Error setting style: {e}", file=sys.stderr)
            return CommandResult(connection, os.EX_OSERR)

    def get_command_name(self) -> str:
        return "set style"

    def get_command_help(self) -> str:
        return """Set the syntax highlighting style for interactive mode.

Usage:
  set style <style_name>

Parameters:
  style_name  Name of the pygments style to use (quote if it contains special characters)

Examples:
  set style default
  set style monokai
  set style 'github-dark'
  set style vim

Note: Style names with hyphens or other special characters should be quoted.
Use 'list styles' to see all available styles.
This setting affects syntax highlighting in interactive mode."""


class SourceHandler(CommandHandler):
    """Handler for SOURCE commands."""

    def __init__(self) -> None:
        self._query_executor: Optional[Callable[..., Any]] = None
        self._line_processor: Optional[Callable[..., Any]] = None

    def set_query_functions(self, query_executor: Callable[..., Any], line_processor: Callable[..., Any]) -> None:
        """Set the query execution and line processing functions."""
        self._query_executor = query_executor
        self._line_processor = line_processor

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 0 and tokens[0].lower() == "source"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        if len(tokens) != 2:
            print("Invalid SOURCE statement", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

        if not self._query_executor or not self._line_processor:
            # Fallback to original logic if functions not set
            return CommandResult(connection, -1)

        try:
            filename = self._unquote(tokens[1])
            with open(filename, mode="r") as f:
                file_content = f.read()

            # Strip shebang line if present to support executable SQL files
            file_content = _strip_shebang(file_content)

            # Process the file content using the injected functions
            (sql_stmt, connection, return_code) = self._line_processor(
                args, connection, file_content, "", history, self._query_executor
            )
            if len(sql_stmt.strip()):
                connection, return_code = self._query_executor(args, connection, sql_stmt, history)
            return CommandResult(connection, return_code)
        except Exception as e:
            print(e, file=sys.stderr)
            return CommandResult(connection, os.EX_OSERR)

    def get_command_name(self) -> str:
        return "source"

    def get_command_help(self) -> str:
        return """Execute SQL commands from a file.

Usage:
  source <filename>

Parameters:
  filename  Path to the SQL file to execute

Examples:
  source "script.sql"
  source '/path/to/queries.sql'

The file can contain multiple SQL statements separated by semicolons.
Shebang lines (#!) at the beginning of files are automatically stripped."""


class ListHandler(CommandHandler):
    """Handler for LIST commands."""

    def __init__(self) -> None:
        self._query_executor: Optional[Callable[..., Any]] = None

    def set_query_functions(self, query_executor: Callable[..., Any], line_processor: Callable[..., Any]) -> None:
        """Set the query execution function."""
        self._query_executor = query_executor

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) > 0 and tokens[0].lower() == "list"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        tokens = [t.lower() for t in tokens]

        # We don't support JDBC verbose option
        if tokens[-1] == "verbose":
            print("List verbose is not supported by pyocient", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

        if not self._query_executor:
            # Fallback to original logic if function not set
            return CommandResult(connection, -1)

        if tokens == ["list", "all", "queries"]:
            connection, return_code = self._query_executor(args, connection, "select * from sys.queries", history)
            return CommandResult(connection, return_code)

        if tokens == ["list", "system", "tables"]:
            query = """select (table_schema || '.' || table_name) as name
                       from information_schema.tables
                       where table_schema in ('sys', 'information_schema')
                       order by name"""
            connection, return_code = self._query_executor(args, connection, query, history)
            return CommandResult(connection, return_code)

        if tokens == ["list", "tables"]:
            query = """select (table_schema || '.' || table_name) as name
                       from information_schema.tables
                       where table_schema not in ('sys', 'information_schema')
                       order by name"""
            connection, return_code = self._query_executor(args, connection, query, history)
            return CommandResult(connection, return_code)

        if tokens == ["list", "views"]:
            query = """select (table_schema || '.' || table_name) as name
                       from information_schema.views
                       where table_schema not in ('sys', 'information_schema')
                       order by name"""
            connection, return_code = self._query_executor(args, connection, query, history)
            return CommandResult(connection, return_code)

        if tokens == ["list", "styles"]:
            # List all available pygments styles with examples
            try:
                from pygments import highlight
                from pygments.formatters import Terminal256Formatter
                from pygments.lexers.sql import SqlLexer

                styles = sorted(get_all_styles())
                sample_sql = "select abc from \"def\" where x = 'ghk' -- sample"
                lexer = SqlLexer()

                for style_name in styles:
                    print(f"\n{style_name}:", file=args.outfile)
                    if args.nocolor:
                        # If nocolor is set, just show the SQL without formatting
                        print(f"  {sample_sql}", file=args.outfile)
                    else:
                        try:
                            formatter = Terminal256Formatter(style=style_name)
                            highlighted = highlight(sample_sql, lexer, formatter)
                            # Indent the highlighted output
                            for line in highlighted.rstrip().split("\n"):
                                print(f"  {line}", file=args.outfile)
                        except Exception:
                            # If a specific style fails, just show the name
                            print(f"  {sample_sql}", file=args.outfile)

                return CommandResult(connection, os.EX_OK)
            except Exception as e:
                print(f"Error listing styles: {e}", file=sys.stderr)
                return CommandResult(connection, os.EX_OSERR)

        # If we get here, it's an unsupported LIST command
        print(f"Unsupported LIST command: {' '.join(tokens)}", file=sys.stderr)
        return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "list"

    def get_command_help(self) -> str:
        return """List database objects and styles.

Usage:
  list all queries     List all running queries
  list system tables   List system tables
  list tables          List user tables
  list views           List user views
  list styles          List available syntax highlighting styles

Examples:
  list tables          # Show all user tables
  list system tables   # Show system tables
  list views           # Show all views
  list all queries     # Show running queries
  list styles          # Show available styles for syntax highlighting"""


class ExpectErrorHandler(CommandHandler):
    """Handler for EXPECT ERROR commands."""

    def __init__(self) -> None:
        self._query_executor: Optional[Callable[..., Any]] = None

    def set_query_functions(self, query_executor: Callable[..., Any], line_processor: Callable[..., Any]) -> None:
        """Set the query execution function."""
        self._query_executor = query_executor

    def can_handle(self, tokens: List[str]) -> bool:
        result = (
            len(tokens) >= 5
            and tokens[0].lower() == "expect"
            and tokens[1].lower() == "error"
            and tokens[3].lower() == "for"
        )
        return result

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        if connection is None:
            print("No active connection", file=sys.stderr)
            return CommandResult(connection, os.EX_UNAVAILABLE)

        if not self._query_executor:
            # Fallback to original logic if function not set
            return CommandResult(connection, -1)

        # Extract expected error code (remove quotes if present)
        expected_error_code = self._unquote(tokens[2])

        # Extract the SQL statement (everything after FOR)
        sql_statement = " ".join(tokens[4:])

        if args.echo:
            print(f"EXPECT ERROR '{expected_error_code}' FOR {sql_statement}", file=args.outfile)

        try:
            cursor = connection.cursor()
            cursor.execute(sql_statement)

            # If we get here, the statement succeeded when it should have failed
            print(f"Expected error '{expected_error_code}' but statement succeeded", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

        except SQLException as e:
            # Check if the error code matches what we expected (try both sql_state and vendor_code)
            if str(e.sql_state) == expected_error_code or str(e.vendor_code) == expected_error_code:
                print("OK", file=args.outfile)
                return CommandResult(connection, os.EX_OK)
            else:
                print(
                    f"Expected error '{expected_error_code}' but got error '{e.sql_state}' (vendor code: {e.vendor_code}): {e.reason}",
                    file=sys.stderr,
                )
                return CommandResult(connection, os.EX_DATAERR)
        except Exception as e:
            print(f"Expected SQL error '{expected_error_code}' but got unexpected error: {e}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "expect error"

    def get_command_help(self) -> str:
        return """Expect a SQL statement to fail with a specific error code.

Usage:
  expect error '<error_code>' for <sql_statement>

Parameters:
  error_code     Expected SQL error code (SQLSTATE or vendor code)
  sql_statement  SQL statement that should fail

Examples:
  expect error '42704' for select nonexistent_column from mytable;
  expect error '42601' for select * from;

The command succeeds if the SQL statement fails with the expected error code.
It fails if the statement succeeds or fails with a different error code."""


class ExpectRowcountHandler(CommandHandler):
    """Handler for EXPECT ROWCOUNT commands."""

    def __init__(self) -> None:
        self._query_executor: Optional[Callable[..., Any]] = None

    def set_query_functions(self, query_executor: Callable[..., Any], line_processor: Callable[..., Any]) -> None:
        """Set the query execution function."""
        self._query_executor = query_executor

    def can_handle(self, tokens: List[str]) -> bool:
        return (
            len(tokens) >= 5
            and tokens[0].lower() == "expect"
            and tokens[1].lower() == "rowcount"
            and tokens[2].isdigit()
            and tokens[3].lower() == "for"
        )

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        if connection is None:
            print("No active connection", file=sys.stderr)
            return CommandResult(connection, os.EX_UNAVAILABLE)

        if not self._query_executor:
            # Fallback to original logic if function not set
            return CommandResult(connection, -1)

        # Extract expected rowcount
        try:
            expected_rowcount = int(tokens[2])
        except ValueError:
            print(f"Invalid rowcount value: {tokens[2]}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

        # Extract the SQL statement (everything after FOR)
        sql_statement = " ".join(tokens[4:])

        if args.echo:
            print(f"EXPECT ROWCOUNT {expected_rowcount} FOR {sql_statement}", file=args.outfile)

        try:
            # Execute the query directly so we can count rows while displaying results
            cursor = connection.cursor()
            cursor.execute(sql_statement)

            # Handle the output based on whether it's a SELECT or not
            if cursor.description is not None:
                # This is a SELECT statement - display results and count rows
                actual_rowcount = 0

                # Use the imported modules for output formatting

                if args.format == "json":
                    results = []
                    while True:
                        rows = cursor.fetchmany(args.rows)
                        if not rows:
                            break
                        for row in rows:
                            results.append({cursor.description[i][0]: row[i] for i in range(len(row))})
                            actual_rowcount += 1

                    print(
                        json.dumps(results, indent=4, ensure_ascii=False, default=custom_type_to_json),
                        file=args.outfile,
                    )

                elif args.format == "table":
                    # For table format, we need to collect all rows first to format properly
                    all_rows = []
                    while True:
                        rows = cursor.fetchmany(args.rows)
                        if not rows:
                            break
                        for row in rows:
                            all_rows.append(row)
                            actual_rowcount += 1

                    # Print table format (simplified version)
                    if all_rows:
                        # Print header
                        headers = [desc[0] for desc in cursor.description]
                        print("\t".join(headers), file=args.outfile)
                        # Print rows
                        for row in all_rows:
                            print("\t".join(str(cell) for cell in row), file=args.outfile)

                elif args.format == "csv":
                    output = io.StringIO()
                    writer = csv.writer(output)

                    # Write header
                    headers = [desc[0] for desc in cursor.description]
                    writer.writerow(headers)

                    # Write rows
                    while True:
                        rows = cursor.fetchmany(args.rows)
                        if not rows:
                            break
                        for row in rows:
                            writer.writerow([str(cell) for cell in row])
                            actual_rowcount += 1

                    print(output.getvalue().rstrip(), file=args.outfile)

                # Print the "Fetched X rows" message if output is to a TTY
                if args.outfile and args.outfile.isatty():
                    print(f"Fetched {actual_rowcount} rows")

            else:
                # This is a non-SELECT statement (DML/DDL)
                actual_rowcount = cursor.rowcount

                # Print the appropriate message for non-SELECT statements
                if actual_rowcount == (2**31 - 1):
                    print(
                        f"Modified at least {actual_rowcount} rows; database cannot report a larger number",
                        file=args.outfile,
                    )
                elif actual_rowcount >= 0:
                    print(f"Modified {actual_rowcount} rows", file=args.outfile)
                else:
                    print("OK", file=args.outfile)

            # Now check if the rowcount matches the expected value
            if actual_rowcount == (2**31 - 1) and expected_rowcount >= (2**31 - 1):
                print("OK", file=args.outfile)
                return CommandResult(connection, os.EX_OK)
            elif actual_rowcount == expected_rowcount:
                print("OK", file=args.outfile)
                return CommandResult(connection, os.EX_OK)
            else:
                print(f"Expected rowcount {expected_rowcount} but got {actual_rowcount} rows", file=sys.stderr)
                return CommandResult(connection, os.EX_DATAERR)

        except Exception as e:
            print(f"SQL error while executing statement: {e}", file=sys.stderr)
            return CommandResult(connection, os.EX_DATAERR)

    def get_command_name(self) -> str:
        return "expect rowcount"

    def get_command_help(self) -> str:
        return """Expect a SQL statement to affect a specific number of rows.

Usage:
  expect rowcount <number> for <sql_statement>

Parameters:
  number         Expected number of affected rows
  sql_statement  SQL statement to execute (DML, DDL, or SELECT)

Examples:
  expect rowcount 1 for insert into mytable values (1, 'test');
  expect rowcount 0 for create user testuser password 'pass123';
  expect rowcount 5 for select * from mytable where status = 'active';
  expect rowcount 2 for update mytable set status = 'inactive' where id < 3;

The command succeeds if the SQL statement affects exactly the expected number of rows.
For SELECT statements, it counts the number of rows returned.
For DDL statements, it typically expects 0 rows affected."""


class CommandRegistry:
    """Registry for command handlers."""

    def __init__(self) -> None:
        self._handlers: List[CommandHandler] = []
        self._query_executor: Optional[Callable[..., Any]] = None
        self._line_processor: Optional[Callable[..., Any]] = None

    def register(self, handler: CommandHandler) -> None:
        """Register a command handler."""
        self._handlers.append(handler)

    def set_query_functions(self, query_executor: Callable[..., Any], line_processor: Callable[..., Any]) -> None:
        """Set the query execution and line processing functions for handlers that need them."""
        self._query_executor = query_executor
        self._line_processor = line_processor

    def find_handler(self, tokens: List[str]) -> Optional[CommandHandler]:
        """Find a handler that can process the given tokens."""
        for handler in self._handlers:
            if handler.can_handle(tokens):
                # Set query functions for handlers that need them
                if hasattr(handler, "set_query_functions"):
                    handler.set_query_functions(self._query_executor, self._line_processor)
                return handler
        return None

    def get_all_handlers(self) -> List[CommandHandler]:
        """Return all registered handlers."""
        return self._handlers.copy()


class HelpHandler(CommandHandler):
    """Handler for HELP commands."""

    def __init__(self, registry: "CommandRegistry") -> None:
        self._registry = registry

    def can_handle(self, tokens: List[str]) -> bool:
        return len(tokens) >= 1 and tokens[0].lower() == "help"

    def handle(
        self, tokens: List[str], args: "Namespace", connection: Optional[Connection], history: Optional[History]
    ) -> CommandResult:
        if len(tokens) == 1:
            # Show list of all commands
            print("Available commands:", file=args.outfile)
            print("", file=args.outfile)

            handlers = self._registry.get_all_handlers()
            # Sort handlers by command name for consistent output
            sorted_handlers = sorted(handlers, key=lambda h: h.get_command_name().lower())

            for handler in sorted_handlers:
                if isinstance(handler, HelpHandler):
                    continue  # Don't include help in the list of commands it shows
                command_name = handler.get_command_name()
                # Get first line of help as brief description
                help_text = handler.get_command_help()
                brief = help_text.split("\n")[0] if help_text else "No description available"
                print(f"  {command_name:<20} {brief}", file=args.outfile)

            print("", file=args.outfile)
            print("Use 'help <command>' for detailed information about a specific command.", file=args.outfile)

        elif len(tokens) >= 2:
            # Show help for specific command (handle multi-word commands)
            # Join all tokens after "help" to form the command name
            command_name = " ".join(tokens[1:]).lower()

            # Limit to reasonable command lengths to avoid abuse
            if len(tokens) > 3:  # help + max 2 words for command (like "set style")
                print("Usage: help [command]", file=sys.stderr)
                return CommandResult(connection, os.EX_USAGE)

            handlers = self._registry.get_all_handlers()
            found_handler = None

            for handler in handlers:
                if handler.get_command_name().lower() == command_name:
                    found_handler = handler
                    break

            if found_handler:
                print(f"Help for '{found_handler.get_command_name()}':", file=args.outfile)
                print("", file=args.outfile)
                print(found_handler.get_command_help(), file=args.outfile)
            else:
                print(f"Unknown command: {command_name}", file=sys.stderr)
                print("Use 'help' to see available commands.", file=sys.stderr)
                return CommandResult(connection, os.EX_USAGE)
        else:
            print("Usage: help [command]", file=sys.stderr)
            return CommandResult(connection, os.EX_USAGE)

        return CommandResult(connection, os.EX_OK)

    def get_command_name(self) -> str:
        return "help"

    def get_command_help(self) -> str:
        return """Show help information for commands.

Usage:
  help           Show list of all available commands
  help <command> Show detailed help for a specific command

Examples:
  help           # List all commands
  help connect   # Show help for the connect command
  help quit      # Show help for the quit command"""


# Global command registry
_command_registry = CommandRegistry()

# Register all command handlers
_command_registry.register(ConnectHandler())
_command_registry.register(QuitHandler())
_command_registry.register(SetFormatHandler())
_command_registry.register(SetEchoHandler())
_command_registry.register(SetTimeHandler())
_command_registry.register(SetStopOnErrorHandler())
_command_registry.register(SetPrintUuidHandler())
_command_registry.register(SetRowsHandler())
_command_registry.register(SetStyleHandler())
_command_registry.register(SourceHandler())
_command_registry.register(ListHandler())
_command_registry.register(ExpectErrorHandler())
_command_registry.register(ExpectRowcountHandler())
_command_registry.register(HelpHandler(_command_registry))


class IgnoreSpaceFileHistory(FileHistory):
    def __init__(self, filename: str):
        super().__init__(filename=filename)

    def _redact_connect_password(self, string: str) -> str:
        # Censors password if given string contains a connect command
        return CONNECT_COMMAND_PATTERN.sub(r"\1*****;\2", string)

    def append_string(self, string: str) -> None:
        # Like the UNIX ignorespace option, causes lines which begin with a
        # white space character to be omitted from the history file.
        if not string[:1].isspace():
            super().append_string(self._redact_connect_password(string))


class ReadOnlyFileHistory(IgnoreSpaceFileHistory):
    def __init__(self, filename: str):
        super().__init__(filename=filename)

    def store_string(self, string: str) -> None:
        pass


if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


def argparser(config: Optional[PyocientConfig] = None) -> "ArgumentParser":
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter

    config_defaults = config.get_defaults() if config else {}

    parser = ArgumentParser(
        description=f"""Ocient Python client {version}.
In the simplest case, run with a Data Source Name (dsn) and a
query.  For example:
  pyocient ocient://user:password@myhost:4050/mydb "select * from mytable"

Multiple query strings may be provided

DSN's are of the form:
  ocient://user:password@[host][:port][/database][?param1=value1&...]

Supported parameter are:

- tls: Which can have the values "off", "unverified", or "on"

- force: true or false to force the connection to stay on this server

- handshake: Which can have the value "cbc"

Multiple hosts may be specified, separated by a comma, in which case the
hosts will be tried in order  Thus an example DSN might be
`ocient://someone:somepassword@host1,host2:4051/mydb`

When running in the command line interface, the following extra commands
are supported:

- connect to 'ocient://....' user someuser using somepassword;

    when the DSN follows the normal pyocient DSN format, but the userid and password may be passed
    using the USER and USING keywords (similar to the Ocient JDBC driver).  The DSN must be quoted.

- source 'file';

    Execute the statements from the specified file.  The file name must be quoted.

- set format table;

    Set the output format

- quit;

Executable SQL Files:
SQL files can be made executable by adding a shebang line at the beginning.

    #!/usr/bin/env -S pyocient -i
    connect to "ocient://user:pass@host/db";
    select * from mytable;

Make the file executable with 'chmod +x script.sql' and run it directly: './script.sql'
The shebang line will be automatically stripped during execution.

""",
        formatter_class=RawDescriptionHelpFormatter,
    )

    # Flags that apply to both execution modes
    outgroup = parser.add_mutually_exclusive_group()
    outgroup.add_argument("-o", "--outfile", type=FileType("w"), default="-", help="Output file")
    outgroup.add_argument(
        "-n",
        "--noout",
        action="store_const",
        const=None,
        dest="outfile",
        help="Do not output results",
    )
    configgroup = parser.add_mutually_exclusive_group()
    configgroup.add_argument(
        "-c",
        "--configfile",
        type=str,
        default=config.config_file if config else str(PyocientConfig.DEFAULT_CONFIG_FILE),
        help="Configuration file",
    )
    configgroup.add_argument(
        "--noconfig",
        action="store_const",
        const=None,
        dest="configfile",
        help="No configuration file",
    )
    parser.add_argument(
        "-i",
        "--infile",
        type=FileType("r"),
        default=None,
        help="Input file containing SQL statements",
    )
    parser.add_argument(
        "-e",
        "--echo",
        action="store_true",
        help="Echo statements in output",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        default=False,
        help="Stop processing on first error during file execution",
    )
    parser.add_argument(
        "-u",
        "--uuid",
        action="store_true",
        help="Print query IDs",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        default="critical",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level, defaults to critical",
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=DEFAULT_FETCH_SIZE,
        help="Number of rows to fetch at a time. Note that for JSON and table format output, the output will appear in blocks of this size",
    )
    parser.add_argument("--logfile", type=FileType("a"), default=sys.stdout, help="Log file")
    parser.add_argument("-t", "--time", action="store_true", help="Output query time")
    parser.add_argument(
        "dsn",
        nargs="?",
        help="DSN of the form ocient://user:password@[host][:port][/database][?param1=value1&...]",
    )
    parser.add_argument("sql", nargs="?", help="SQL statement")
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "table", "csv"],
        default=config_defaults.get("format", "json"),
        help="Output format, defaults to json",
    )
    parser.add_argument(
        "--nocolor",
        action="store_true",
        default=config_defaults.get("nocolor", False),
        help="When using pyocient interactively, do not color",
    )
    parser.add_argument(
        "--style",
        type=str,
        default=config_defaults.get("style", "default"),
        help="When using pyocient interactively, set the style of the prompt",
    )
    parser.add_argument(
        "--nohistory",
        action="store_true",
        default=config_defaults.get("nohistory", False),
        help="When using pyocient interactively, do not store command history",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print current version and exit",
    )

    return parser


def main() -> int:
    import argparse
    import csv
    import json
    from argparse import Namespace

    from pygments.lexers.sql import SqlLexer
    from pygments.token import Token
    from tabulate import tabulate

    # Parse configuration early from command line arguments
    config_file, use_config = PyocientConfig.parse_early_args(sys.argv[1:])
    config = PyocientConfig(config_file, use_config)

    try:
        args = argparser(config).parse_args(sys.argv[1:])
    except SystemExit as e:
        return os.EX_USAGE

    if args.version:
        print(f"Ocient Python client {version}", file=args.outfile)
        return os.EX_OK

    log_level = getattr(logging, args.loglevel.upper(), None)

    # Save away the original showwwarnings function
    original_showwarning = warnings.showwarning

    # Convert pyocient warnings to simple text
    def cli_showwarning(
        message: Any,
        category: Type[Warning],
        filename: str,
        lineno: int,
        file: Optional[TextIO] = None,
        line: Optional[str] = None,
    ) -> None:
        if isinstance(message, OcientWarning):
            print(message.reason, file=args.outfile)
        else:
            original_showwarning(message, category, filename, lineno, file, line)

    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.loglevel}")

    logging.basicConfig(
        level=log_level,
        stream=args.logfile,
        format="[%(asctime)s][%(levelname)s] %(message)s",
    )

    sql_stmt = ""
    in_dollar_quoted_string = False
    lexer = SqlLexer()

    def _unquote(input: str) -> str:
        """
        Unquote a string, with either single or double quotes
        """
        if input[0] == '"' and input[-1] == '"':
            return input[1:-1]
        if input[0] == "'" and input[-1] == "'":
            return input[1:-1]
        return input

    def _do_line(
        args: Namespace,
        connection: Optional[Connection],
        text: str,
        sql_stmt: str,
        history: Optional[History],
        query_fn: Callable[[Namespace, Optional[Connection], str, Optional[History]], Tuple[Optional[Connection], int]],
    ) -> Tuple[str, Optional[Connection], int]:
        nonlocal in_dollar_quoted_string
        new_connection = connection
        return_code = os.EX_OK
        prev_token_val = None

        for token_type, token_val in lexer.get_tokens(text):
            if token_val == "$" and prev_token_val == "$":
                prev_token_val = None
                in_dollar_quoted_string = not in_dollar_quoted_string
                sql_stmt += token_val
                continue

            if token_type == Token.Punctuation and token_val == ";" and not in_dollar_quoted_string:
                (new_connection, return_code) = query_fn(args, new_connection, sql_stmt, history)
                sql_stmt = ""

                # Check if we should stop on error
                if hasattr(args, "stop_on_error") and args.stop_on_error and return_code != os.EX_OK:
                    # Stop processing immediately on error
                    return (sql_stmt, new_connection, return_code)
            else:
                sql_stmt += token_val

            prev_token_val = token_val

        return (sql_stmt, new_connection, return_code)

    def _do_query(
        args: Namespace, connection: Optional[Connection], query: str, history: Optional[History]
    ) -> Tuple[Optional[Connection], int]:
        if args.echo and query.strip():
            # Clean up the query for echoing - remove leading/trailing whitespace but preserve line structure
            lines = query.strip().split("\n")
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned_query = "\n".join(cleaned_lines) if len(cleaned_lines) > 1 else " ".join(query.split())
            print(cleaned_query, file=args.outfile)

        # Set query functions on the registry for handlers that need them
        _command_registry.set_query_functions(_do_query, _do_line)

        # First, see if this is something we should handle here in the CLI
        # First pass: get basic tokens to check if this is EXPECT ROWCOUNT
        basic_tokens = [
            token
            for (token_type, token) in lexer.get_tokens(query)
            if token_type
            in (
                Token.Keyword,
                Token.Name,
                Token.Literal.String.Symbol,
                Token.Literal.String.Single,
                Token.Literal.Number.Integer,
            )
        ]

        # If this is EXPECT ROWCOUNT, include punctuation and operators for better SQL reconstruction
        if (
            len(basic_tokens) >= 3
            and basic_tokens[0].lower() == "expect"
            and basic_tokens[1].lower() == "rowcount"
            and basic_tokens[2].isdigit()
        ):
            tokens = [
                token
                for (token_type, token) in lexer.get_tokens(query)
                if token_type
                in (
                    Token.Keyword,
                    Token.Name,
                    Token.Literal.String.Symbol,
                    Token.Literal.String.Single,
                    Token.Literal.Number.Integer,
                    Token.Punctuation,
                    Token.Operator,
                )
            ]
        else:
            tokens = basic_tokens

        # Try to find a command handler for this query
        handler = _command_registry.find_handler(tokens)
        if handler:
            command_result = handler.handle(tokens, args, connection, history)
            # Handle fallback case for handlers that need original logic
            if command_result.return_code == -1:
                # Fall through to original logic below
                pass
            else:
                return (command_result.connection, command_result.return_code)

        if connection is None:
            print(f"No active connection", file=sys.stderr)
            return (connection, os.EX_UNAVAILABLE)

        # OK, if we fall through to here, have the normal library handle it
        if args.time:
            starttime = time_ns()

        cursor = connection.cursor()

        result: Optional[List[NamedTuple]]
        try:
            cursor.execute(query)

            if cursor.description:
                result = cursor.fetchmany(args.rows)
            else:
                result = None
        except SQLException as e:
            print(e, file=sys.stderr)
            return (cursor.connection, os.EX_DATAERR)
        except IOError as exc:
            print(f"I/O Error: {exc}")
            return (connection, os.EX_IOERR)
        except KeyboardInterrupt:
            print("Operation interrupted.", file=sys.stderr)
            cur_conn = cursor.connection
            cur_conn.close()
            cur_conn.reconnect(security_token=cur_conn.security_token)
            return (cur_conn, os.EX_IOERR)

        if args.time:
            endtime = time_ns()

        if cursor.description is None:
            if cursor.rowcount == (2**31 - 1):
                print(
                    f"Modified at least {cursor.rowcount} rows; database cannot report a larger number",
                    file=args.logfile,
                )
            elif cursor.rowcount >= 0:
                print(f"Modified {cursor.rowcount} rows", file=args.outfile)
            else:
                print("OK", file=args.outfile)

        elif args.outfile is not None:
            colnames = [c[0] for c in cursor.description]
            binary_column_idxs = [i for i, col in enumerate(cursor.description) if col[1] == TypeCodes.BINARY]

            if cursor.generated_result and cursor.description[0][0] == "explain":
                to_dump = [{"explain": json.loads(cursor.generated_result)}]

                print(
                    json.dumps(to_dump, indent=4, ensure_ascii=False, default=custom_type_to_json),
                    file=args.outfile,
                )
                result = None

            while result:
                # Preprocess bytes objects into desired str output, default to hex
                if binary_column_idxs:
                    for i, row in enumerate(result):
                        for col_idx in binary_column_idxs:
                            col = row[col_idx]
                            if col is not None:
                                assert isinstance(col, bytes)
                                # N.B. this line relies on the assumption (true today) that
                                #      the NamedTuple `_fields` are in the same order as the
                                #      `cursor.description` tuples. This assumption allows
                                #      this line to look up the NamedTuple field name, which
                                #      importantly may differ from the column name due to
                                #      `rename=True` in the NamedTuple constructor, by its
                                #      column index.
                                result[i] = row._replace(**{row._fields[col_idx]: col.hex()})

                if args.format == "json":
                    if colnames:
                        dict_result = [{colnames[i]: val for (i, val) in enumerate(row)} for row in result]
                    else:
                        dict_result = [row._asdict() for row in result]

                    print(
                        json.dumps(dict_result, indent=4, ensure_ascii=False, default=custom_type_to_json),
                        file=args.outfile,
                    )
                elif args.format == "table":
                    print(
                        tabulate(result, headers=colnames, tablefmt="psql", missingval="NULL"),
                        file=args.outfile,
                    )
                elif args.format == "csv":
                    if colnames:
                        csv.writer(args.outfile, quoting=csv.QUOTE_ALL).writerow(colnames)
                    writer = csv.writer(args.outfile)
                    for row in result:
                        writer.writerow(row)

                colnames = []
                result = cursor.fetchmany(args.rows)

        if args.time:
            endtime = time_ns()
            print(f"Execution time: {(endtime - starttime) / 1000000000:.3f} seconds", file=args.outfile)

        if args.uuid and cursor.query_id:
            print(f"Query UUID: '{cursor.query_id}'", file=args.outfile)

        if cursor.description and args.outfile and args.outfile.isatty():
            print(f"Fetched {cursor.rowcount} rows")
        # If we don't return this connection, then we end up using the old connection which we could have been redirected
        return (cursor.connection, os.EX_OK)

    def _do_repl(args: Namespace, connection: Optional[Connection]) -> None:
        from pathlib import Path

        from prompt_toolkit import PromptSession
        from prompt_toolkit.lexers import PygmentsLexer
        from prompt_toolkit.styles import style_from_pygments_cls
        from pygments.styles import get_style_by_name

        sql_stmt = ""

        from pathlib import Path

        history: Union[ReadOnlyFileHistory, IgnoreSpaceFileHistory]
        if args.nohistory:
            history = ReadOnlyFileHistory(str(PyocientConfig.DEFAULT_HISTORY_FILE))
        else:
            history = IgnoreSpaceFileHistory(str(PyocientConfig.DEFAULT_HISTORY_FILE))

        # Helper function to create a new session with the current style
        def create_session() -> PromptSession[str]:
            if args.nocolor:
                return PromptSession(history=history)
            else:
                style = style_from_pygments_cls(get_style_by_name(args.style))
                return PromptSession(
                    lexer=PygmentsLexer(SqlLexer),
                    style=style,
                    history=history,
                )

        session = create_session()
        current_style = args.style

        if connection:
            cursor = connection.cursor()
            print(f"Ocient Hyperscale Data Warehouse™", file=args.outfile)
            print(f"System Version: {cursor.getSystemVersion()}, Client Version {version}", file=args.outfile)
        eof = False
        text = ""
        while not eof:
            # Check if style has changed and recreate session if needed
            if current_style != args.style:
                session = create_session()
                current_style = args.style

            try:
                text = session.prompt("> ")
            except KeyboardInterrupt:
                sql_stmt = ""
                continue
            except EOFError:
                break
            (sql_stmt, connection, return_code) = _do_line(args, connection, text, sql_stmt, history, _do_query)

        if len(sql_stmt.strip()):
            (connection, return_code) = _do_query(args, connection, sql_stmt, history)

        print("GoodBye!", file=args.outfile)

    return_code = os.EX_OK
    connection = None
    try:
        with warnings.catch_warnings():
            # Replace the warnings function with our custom one
            warnings.showwarning = cli_showwarning

            if args.dsn:
                connection = connect(args.dsn, configfile=args.configfile)

            if args.sql:
                (connection, return_code) = _do_query(args, connection, args.sql, None)
            elif args.infile:
                file_content = args.infile.read()
                file_content = _strip_shebang(file_content)
                (sql_stmt, connection, return_code) = _do_line(
                    args, connection, file_content, sql_stmt, None, _do_query
                )
                if len(sql_stmt.strip()):
                    (connection, return_code) = _do_query(args, connection, sql_stmt, None)
            elif sys.stdin.isatty():
                _do_repl(args, connection)
            else:
                stdin_content = sys.stdin.read()
                stdin_content = _strip_shebang(stdin_content)
                (sql_stmt, connection, return_code) = _do_line(
                    args, connection, stdin_content, sql_stmt, None, _do_query
                )
                if len(sql_stmt.strip()):
                    (connection, return_code) = _do_query(args, connection, sql_stmt, None)

    except SQLException as exc:
        print(f"Error: {exc.reason}", file=sys.stderr)
        return_code = os.EX_DATAERR
    except EOFError:
        return_code = os.EX_OK
    except IOError as exc:
        print(f"I/O Error: {exc}")
        return_code = os.EX_IOERR
    finally:
        if connection:
            try:
                connection.close()
            except SQLException:
                pass

    return return_code


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
