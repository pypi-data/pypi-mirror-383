"""Python Database API for the Ocient Hyperscale Data Warehouse

This python database API conforms to the Python Database API
Specification 2.0 and can be used to access the Ocient Hyperscale Data Warehouse.

This module can also be called as a main function, in which case
it acts as a primitive CLI for the database.

When called as main, it a connection string in DSN (data source name)
format, followed by zero or more query strings that will be executed.
Output is returned in JSON format.

The Ocient DSN is of the format:
   `ocient://user:password@[host][:port][/database][?param1=value1&...]`

`user` and `password` must be supplied.  `host` defaults to localhost,
port defaults to 4050, database defaults to `system` and `tls` defaults
to `off`.

Multiple hosts may be specified, separated by a comma, in which case the
hosts will be tried in order  Thus an example DSN might be
`ocient://someone:somepassword@host1,host2:4051/mydb`

Currently supported parameters are:

- tls: Which can have the values "off", "unverified", or "on"
- force: true or false to force the connection to stay on this server

Any warnings returned by the database are sent to the python warnings
module.  By default that module sends warnings to stdout, however
the behaviour can be changed by using that module.
"""

# Explicitly re-export PEP 249 module interface,
# along with some extras (MalformedURL) for backwards import compatibility,
# plus __version__ and __version_info__ which are conventions, but not requirements.

from pyocient.api import (
    BINARY,
    DATETIME,
    NUMBER,
    ROWID,
    STRING,
    Binary,
    Connection,
    Cursor,
    DatabaseError,
    DataError,
    Date,
    DateFromTicks,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    MalformedURL,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    SecurityToken,
    SQLException,
    SSORedirection,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
    TypeCodes,
    Warning,
    apilevel,
    connect,
    custom_type_to_json,
    logger,
    paramstyle,
    threadsafety,
)
from pyocient.datetime_ns import datetime_ns
from pyocient.pkg_version import __version__

__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())

__all__ = [
    "BINARY",
    "DATETIME",
    "NUMBER",
    "ROWID",
    "STRING",
    "Binary",
    "Connection",
    "Cursor",
    "DatabaseError",
    "DataError",
    "Date",
    "DateFromTicks",
    "Error",
    "IntegrityError",
    "InterfaceError",
    "InternalError",
    "MalformedURL",
    "NotSupportedError",
    "OperationalError",
    "ProgrammingError",
    "SecurityToken",
    "SQLException",
    "SSORedirection",
    "Time",
    "TimeFromTicks",
    "Timestamp",
    "TimestampFromTicks",
    "TypeCodes",
    "Warning",
    "apilevel",
    "connect",
    "custom_type_to_json",
    "datetime_ns",
    "logger",
    "paramstyle",
    "threadsafety",
]
