# Lots of names/attributes in message definitions are not visible to mypy. This
# is a catch-all that makes mypy not complain about the usage of names or
# attributes that do not seem to be defined. Unfortunately, I have not found a
# comment syntax that scopes this specifically to the "proto" import(s).
# mypy: disable-error-code="attr-defined,name-defined"


from __future__ import annotations

import base64
import binascii
import configparser
import datetime
import decimal
import hashlib
import hmac
import ipaddress
import logging
import os
import platform
import re
import shlex
import socket
import ssl
import struct
import sys
import typing
import uuid
from collections import namedtuple
from dataclasses import dataclass
from enum import IntEnum
from math import isinf
from time import sleep
from types import TracebackType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    Generic,
    Iterable,
    List,
    Literal,
    Mapping,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from warnings import warn

import asn1  # type: ignore[import-untyped]
import dsnparse  # type: ignore[import-untyped]
import pyparsing as pp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.message import Message
from typing_extensions import Self, TypeGuard

# Note: Because we copy this file it has potential issues within Ocient's private build environment.
# It is not an issue for real uses of the code, but care should be taken internally
import pyocient.ocient_protocol_pb2 as proto
from pyocient import sso
from pyocient.datetime_ns import datetime_ns
from pyocient.pkg_version import __version__ as version

_T = TypeVar("_T")
_MsgT = TypeVar("_MsgT", bound=Message)

logger = logging.getLogger("pyocient")

# See PEP 249 for the values of these attributes
apilevel = "2.0"  # pylint: disable=invalid-name
threadsafety = 1  # pylint: disable=invalid-name
paramstyle = "pyformat"  # pylint: disable=invalid-name
DRIVER_ID = "pyocient"
PROTOCOL_VERSION = "8.0.0"
SESSION_EXPIRED_CODE = -733

SSO_RESPONSE_TIMEOUT = 60.0

parts = version.split(".")
version_major = int(parts[0])
version_minor = int(parts[1])
version_patch = parts[2]

_OID_RSA_DH = "1.2.840.113549.1.3.1"
"""
OID for RSA with Diffie-Hellman
https://oidref.com/1.2.840.113549.1.3
"""

# Singleton for parameterless queries
NoParams: object = object()


@dataclass
class SQLException(Exception):
    """Base exception for all Ocient exceptions.

    Attributes:

    - sql_state: The SQLSTATE defined in the SQL standard
    - reason: A string description of the exception
    - vendor_code: An Ocient specific error code
    """

    reason: str = "The operation completed successfully"
    sql_state: str = "00000"
    vendor_code: int = 0

    def __str__(self) -> str:
        return f"State: {self.sql_state} Code: {self.vendor_code} Reason: {self.reason}"


#########################################################################
# Database API 2.0 exceptions.  These are required by PEM 249
#########################################################################


class Error(SQLException):
    """Exception that is the base class of all other error exceptions."""

    def __init__(self, reason: str, sql_state: str = "58005", vendor_code: int = -100) -> None:
        super().__init__(reason, sql_state=sql_state, vendor_code=vendor_code)


class Warning(SQLException, UserWarning):  # pylint: disable=redefined-builtin
    """Exception that is the base class of all other warning exceptions."""


class InterfaceError(Error):
    """Exception raised for errors that are related to the
    database interface rather than the database itself.
    """


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore
    """


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not found.
    """


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors, e.g. table not found,
    syntax error in the SQL statement, wrong number of parameters
    specified, etc.
    """


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database
    is affected, e.g. a foreign key check fails
    """


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the
    processed data like division by zero, numeric value out of range, etc.
    """


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not
    supported by the database
    """


class MalformedURL(DatabaseError):
    """Exception raised in case a malformed DSN is received"""

    def __init__(self, reason: str) -> None:
        super().__init__(sql_state="08001", vendor_code=-200, reason=reason)


class SSORedirection(Exception):
    """Exception raised when SSO redirection is required

    It contains the URL from which to request authentication
    The response will redirect back to the sso_redirect_url, and
    will contain `code` and `state` fields, which in turn should be

    passed back into a new connect call as the sso_code and sso_state
    paramters.
    """

    def __init__(self, authURL: str, state: Dict[Any, Any]):
        self.authURL = authURL
        self.state = state


class TypeCodes(IntEnum):
    """
    Database column type codes
    """

    DEM = 0
    INT = 1
    LONG = 2
    FLOAT = 3
    DOUBLE = 4
    STRING = 5
    CHAR = 5
    TIMESTAMP = 6
    NULL = 7
    BOOLEAN = 8
    BINARY = 9
    BYTE = 10
    SHORT = 11
    TIME = 12
    DECIMAL = 13
    ARRAY = 14
    UUID = 15
    ST_POINT = 16
    IP = 17
    IPV4 = 18
    DATE = 19
    TIMESTAMP_NANOS = 20
    TIME_NANOS = 21
    TUPLE = 22
    ST_LINESTRING = 23
    ST_POLYGON = 24
    ST_POLYGON_FULLFLAG = 25

    @classmethod
    def cls_to_type(cls, pclass: object) -> TypeCodes:
        if pclass == str:
            return cls.STRING
        elif pclass == int:
            return cls.INT
        elif pclass == float:
            return cls.FLOAT
        elif pclass == uuid.UUID:
            return cls.UUID
        elif pclass == Optional[uuid.UUID]:
            return cls.UUID
        raise Error(f"Unknown column class {pclass}")


# By instantiating these here we reduce the overhead of setting this up
# each time we call it
_unpack_short = struct.Struct("!h").unpack_from
_unpack_int = struct.Struct("!i").unpack_from
_unpack_long = struct.Struct("!q").unpack_from
_unpack_float = struct.Struct("!f").unpack_from
_unpack_double = struct.Struct("!d").unpack_from
_unpack_bool = struct.Struct("?").unpack_from
_unpack_char = struct.Struct("c").unpack_from

# easy conversions we can do with structs
_type_map = {
    TypeCodes.INT.value: (struct.calcsize("!i"), _unpack_int),
    TypeCodes.LONG.value: (struct.calcsize("!q"), _unpack_long),
    TypeCodes.FLOAT.value: (struct.calcsize("!f"), _unpack_float),
    TypeCodes.DOUBLE.value: (struct.calcsize("!d"), _unpack_double),
    TypeCodes.BOOLEAN.value: (struct.calcsize("?"), _unpack_bool),
    TypeCodes.SHORT.value: (struct.calcsize("!h"), _unpack_short),
}


#########################################################################
# Database API 2.0 types.  These are required by PEM 249
#########################################################################
Binary = bytes  # : :meta private:
STRING = TypeCodes.STRING.value  # : :meta private:
BINARY = TypeCodes.BINARY.value  # : :meta private:
NUMBER = TypeCodes.INT.value  # : :meta private:
DATETIME = TypeCodes.TIMESTAMP.value  # : :meta private:
ROWID = TypeCodes.INT.value  # : :meta private:


#########################################################################
# Lightweight GIS classes
#########################################################################

_EMPTY_LITERAL = "EMPTY"
_EMPTY_KEYWORD = pp.CaselessKeyword(_EMPTY_LITERAL)
_FULL_LITERAL = "FULL"
_FULL_KEYWORD = pp.CaselessKeyword(_FULL_LITERAL)
_OPEN_PAREN = pp.Literal("(").suppress()
_CLOSE_PAREN = pp.Literal(")").suppress()


class STPoint:
    EMPTY: "STPoint"
    _PARSER = pp.CaselessKeyword("POINT").suppress() + pp.Or(
        (_EMPTY_KEYWORD, _OPEN_PAREN + pp.common.fnumber[2] + _CLOSE_PAREN)
    )

    def __init__(self, long: float, lat: float) -> None:
        self.long = long
        self.lat = lat

    def wkt_inner(self) -> str:
        return str(self.long) + " " + str(self.lat)

    def __repr__(self) -> str:
        if isinf(self.long) or isinf(self.lat):
            return "POINT EMPTY"
        return "POINT(" + self.wkt_inner() + ")"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, STPoint):
            return self.long == other.long and self.lat == other.lat
        return NotImplemented

    @classmethod
    def from_wkt_str(cls, point_wkt: str) -> STPoint:
        """
        Converts wkt representation of STPoint to STPoint
        e.g. "POINT(3.0 3.0)"
        """
        try:
            parse_results = cls._PARSER.parse_string(point_wkt)
            if parse_results.as_list() == [_EMPTY_LITERAL]:
                return cls.EMPTY
            else:
                long, lat = parse_results
                return cls(long=long, lat=lat)
        except pp.exceptions.ParseException as e:
            raise ValueError(f"{point_wkt} not valid representation of STPoint") from e


STPoint.EMPTY = STPoint(float("inf"), float("inf"))


def _linestring_wkt_inner(points: List[STPoint]) -> str:
    return "(" + ", ".join((p.wkt_inner() for p in points)) + ")"


class STLinestring:
    EMPTY: "STLinestring"
    _PARSER = pp.CaselessKeyword("LINESTRING").suppress() + pp.Or(
        (_EMPTY_KEYWORD, _OPEN_PAREN + pp.DelimitedList(pp.Group(pp.common.fnumber[2]), delim=",") + _CLOSE_PAREN)
    )

    def __init__(self, points: List[STPoint]) -> None:
        self.points = points

    def __repr__(self) -> str:
        if not self.points:
            return "LINESTRING EMPTY"
        return "LINESTRING" + _linestring_wkt_inner(self.points)

    def __eq__(self, other: object) -> bool:
        # strict equality, not semantic
        if isinstance(other, STLinestring):
            return self.points == other.points
        return NotImplemented

    @classmethod
    def from_wkt_str(cls, linestring_wkt: str) -> STLinestring:
        """
        Converts wkt representation of STLinestring to STLinestring
        e.g. "LINESTRING(3.0 3.0, 6.0 6.0)"
        """
        try:
            parse_results = cls._PARSER.parse_string(linestring_wkt)
            if parse_results.as_list() == [_EMPTY_LITERAL]:
                return cls.EMPTY
            else:
                points = [STPoint(long, lat) for long, lat in parse_results]
                return cls(points=points)
        except pp.exceptions.ParseException as e:
            raise ValueError(f"{linestring_wkt} not valid representation of STLinestring") from e


STLinestring.EMPTY = STLinestring(points=[])


class STPolygon:
    EMPTY: "STPolygon"
    FULL: "STPolygon"
    _PARSER = pp.CaselessKeyword("POLYGON").suppress() + pp.Or(
        (
            _EMPTY_KEYWORD,
            _FULL_KEYWORD,
            _OPEN_PAREN
            + pp.DelimitedList(
                pp.Group(_OPEN_PAREN + pp.DelimitedList(pp.Group(pp.common.fnumber[2]), delim=",") + _CLOSE_PAREN),
                delim=",",
            )
            + _CLOSE_PAREN,
        )
    )

    def __init__(self, exterior: List[STPoint], holes: List[List[STPoint]], fullFlag: bool) -> None:
        self.exterior = exterior
        self.holes = holes
        self.fullFlag = fullFlag

    def __repr__(self) -> str:
        if self.fullFlag:
            return "POLYGON FULL"
        if not self.exterior:
            return "POLYGON EMPTY"
        return "POLYGON(" + ", ".join((_linestring_wkt_inner(pl) for pl in [self.exterior] + self.holes)) + ")"

    def __eq__(self, other: object) -> bool:
        # strict equality, not semantic
        if isinstance(other, STPolygon):
            return self.exterior == other.exterior and self.holes == other.holes and self.fullFlag == other.fullFlag
        return NotImplemented

    @classmethod
    def from_wkt_str(cls, polygon_wkt: str) -> STPolygon:
        """
        Converts wkt representation of STPolygon to STPolygon
        e.g. "POLYGON((3.0 3.0, -3.0 3.0, 3.0 -3.0))" or
        "POLYGON((3.0 3.0, -3.0 3.0, 3.0 -3.0), (1.0 1.0, -1.0 1.0, 1.0 -1.0))"
        """
        try:
            parse_results = cls._PARSER.parse_string(polygon_wkt)
            if parse_results.as_list() == [_FULL_LITERAL]:
                return cls.FULL
            if parse_results.as_list() == [_EMPTY_LITERAL]:
                return cls.EMPTY
            else:
                exterior_points, *holes_points = parse_results
                exterior = [STPoint(long, lat) for long, lat in exterior_points]
                holes = [[STPoint(long, lat) for long, lat in hole_points] for hole_points in holes_points]
                return cls(exterior=exterior, holes=holes, fullFlag=False)
        except pp.exceptions.ParseException as e:
            raise ValueError(f"{polygon_wkt} not valid representation of STPolygon") from e


STPolygon.EMPTY = STPolygon(exterior=[], holes=[], fullFlag=False)
STPolygon.FULL = STPolygon(exterior=[], holes=[], fullFlag=True)

#########################################################################
# Version class, intended to mirror version_t in build_info.h
#########################################################################


@dataclass(order=True, frozen=True)
class OcientVersion:
    major: int
    minor: int
    patch: int

    _pattern: ClassVar[re.Pattern[str]] = re.compile(r"^\s*(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\s*$")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, version_string: str) -> Self:
        match = cls._pattern.fullmatch(version_string)
        if match is None:
            raise ValueError(f"Can't parse a version from '{version_string}'")

        major_text = match.group("major")
        assert isinstance(major_text, str)  # "major" is not an optional group in cls._pattern
        minor_text = match.group("minor")
        assert isinstance(minor_text, str)  # "minor" is not an optional group in cls._pattern
        patch_text = match.group("patch")
        assert isinstance(patch_text, str)  # "patch" is not an optional group in cls._pattern

        try:
            major = int(major_text)
            minor = int(minor_text)
            patch = int(patch_text)
        except ValueError as e:
            raise ValueError(
                f"Failed to convert version parts '{major_text}', '{minor_text}', and '{patch_text}' to integers"
            ) from e

        return cls(major, minor, patch)


#########################################################################
# Build supported request/response type mappings
#########################################################################


class _OcientRequestFactory(Generic[_T]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated request protobuf"""
        raise NotImplementedError

    def response(self) -> _T:
        """Generates a fully populated response protobuf"""
        raise NotImplementedError

    def process(self, rsp: _T) -> Any:
        """Process the client response"""
        raise NotImplementedError


class _ExecuteQueryFactory(_OcientRequestFactory[proto.ExecuteQueryResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_QUERY")
        req.execute_query.sql = operation
        req.execute_query.force = False
        return req

    def response(self) -> proto.ExecuteQueryResponse:
        """Generates a fully populated EXECUTE_QUERY response protobuf"""
        return proto.ExecuteQueryResponse()


class _ExecuteExplainFactory(_OcientRequestFactory[proto.ExplainResponseStringPlan]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_EXPLAIN request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_EXPLAIN")
        req.execute_explain.format = proto.ExplainFormat.JSON
        splitted = operation.split(maxsplit=1)
        if len(splitted) == 2:
            req.execute_explain.sql = splitted[1]
        return req

    def response(self) -> proto.ExplainResponseStringPlan:
        """Generates a fully populated EXECUTE_EXPLAIN response protobuf"""
        return proto.ExplainResponseStringPlan()


class _ExecuteExportFactory(_OcientRequestFactory[proto.ExecuteExportResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_EXPORT request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_EXPORT")
        req.execute_export.sql = operation
        return req

    def response(self) -> proto.ExecuteExportResponse:
        """Generates a fully populated EXECUTE_EXPORT response protobuf"""
        return proto.ExecuteExportResponse()


class _ExplainPipelineFactory(_OcientRequestFactory[proto.ExplainPipelineResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXPLAIN_PIPELINE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXPLAIN_PIPELINE")
        req.explain_pipeline.sql = operation
        return req

    def response(self) -> proto.ExplainPipelineResponse:
        """Generates a fully populated EXPLAIN_PIPELINE response protobuf"""
        return proto.ExplainPipelineResponse()


class _ForceExternalFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated FORCE_EXTERNAL request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_PARAMETER")
        sp = req.set_parameter
        if operation.endswith("on"):
            sp.force_external.is_on = True
        elif operation.endswith("off"):
            sp.force_external.is_on = False
        else:
            raise ProgrammingError('Format must be "FORCE EXTERNAL (on|off)"')
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates a fully populated FORCE_EXTERNAL response protobuf"""
        return proto.ConfirmationResponse()


class _SetSchemaFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, schema: str) -> proto.Request:
        """Generates a fully populated SET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_SCHEMA")
        req.set_schema.schema = schema
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _GetSchemaFactory(_OcientRequestFactory[proto.GetSchemaResponse]):
    def request(self) -> proto.Request:  # type: ignore[override]
        """Generates a fully populated GET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("GET_SCHEMA")
        return req

    def response(self) -> proto.GetSchemaResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.GetSchemaResponse()


class _ClearCacheFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self) -> proto.Request:  # type: ignore[override]
        """Generates a fully populated CLEAR CACHE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CLEAR_CACHE")
        req.clear_cache.all_nodes = True
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _SetParameterFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, op: str, val: Union[int, str, float]) -> proto.Request:  # type: ignore[override]
        """Generates a fully populated SET PARAMETER request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_PARAMETER")

        sp = req.set_parameter

        if type(val) == str and val.lower() == "reset":
            # Resets handled in cmdCompServer. Set val to 0 as a Parameter still needs to be set for flow control, and most require number values
            sp.reset = True
            if op in ["MAXROWS", "MAXTIME", "MAXTEMPDISK", "PARALLELISM", "ADJUSTTIME"]:
                val = 0
            elif op in ["PRIORITY", "ADJUSTFACTOR"]:
                val = 0.0

        # Set the appropriate parameter
        # proto field assignments are type checked at runtime
        if op == "MAXROWS":
            assert isinstance(val, int)
            sp.row_limit.rowLimit = val
        elif op == "MAXTIME":
            assert isinstance(val, int)
            sp.time_limit.timeLimit = val
        elif op == "MAXTEMPDISK":
            assert isinstance(val, int)
            sp.temp_disk_limit.tempDiskLimit = val
        elif op == "PRIORITY":
            assert isinstance(val, float)
            sp.priority.priority = val
        elif op == "PARALLELISM":
            assert isinstance(val, int)
            sp.concurrency.concurrency = val
        elif op == "SERVICECLASS":
            assert isinstance(val, str)
            sp.service_class_name.service_class_name = val
        elif op == "ADJUSTFACTOR":
            assert isinstance(val, float)
            sp.priority_adjust_factor.priority_adjust_factor = val
        elif op == "ADJUSTTIME":
            assert isinstance(val, int)
            sp.priority_adjust_time.priority_adjust_time = val
        else:
            raise ProgrammingError(reason=f"Syntax error. Invalid SET {op}")

        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates a SET_PARAMETER response protobuf"""
        return proto.ConfirmationResponse()


class _CancelQueryFactory(_OcientRequestFactory[proto.CancelQueryResponse]):
    def request(self, id: str) -> proto.Request:
        """Generates a fully populated CANCEL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CANCEL_QUERY")
        req.cancel_query.sql = id
        return req

    def response(self) -> proto.CancelQueryResponse:
        """Generates a CANCEL_QUERY response protobuf"""
        return proto.CancelQueryResponse()


class _KillQueryFactory(_OcientRequestFactory[proto.KillQueryResponse]):
    def request(self, id: str) -> proto.Request:
        """Generates a fully populated KILL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("KILL_QUERY")
        req.kill_query.sql = id
        return req

    def response(self) -> proto.KillQueryResponse:
        """Generates a KILL_QUERY response protobuf"""
        return proto.KillQueryResponse()


class _GetSystemMetadataFactory(_OcientRequestFactory[proto.FetchSystemMetadataResponse]):
    def request(  # type: ignore[override]
        self,
        op: proto.FetchSystemMetadata.SystemMetadataCall,
        schema: Optional[str],
        table: Optional[str],
        column: Optional[str],
        view: Optional[str],
    ) -> proto.Request:
        """Generates a fully populated GET_SYSTEM_METADATA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("FETCH_SYSTEM_METADATA")
        req.fetch_system_metadata.call = op

        if schema is not None:
            req.fetch_system_metadata.schema = schema
        if table is not None:
            req.fetch_system_metadata.table = table
        if column is not None:
            req.fetch_system_metadata.column = column
        if view is not None:
            req.fetch_system_metadata.view = view

        return req

    def response(self) -> proto.FetchSystemMetadataResponse:
        """Generates a fully populated GET_SYSTEM_METADATA response protobuf"""
        return proto.FetchSystemMetadataResponse()


_OCIENT_REQUEST_FACTORIES: Mapping[str, _OcientRequestFactory[Any]] = {
    "SELECT": _ExecuteQueryFactory(),
    "PREVIEW": _ExecuteQueryFactory(),
    "WITH": _ExecuteQueryFactory(),
    "SHOW": _ExecuteQueryFactory(),
    "DESCRIBE": _ExecuteQueryFactory(),
    "EXPLAIN PIPELINE": _ExplainPipelineFactory(),
    "EXPLAIN": _ExecuteExplainFactory(),
    "EXPORT": _ExecuteExportFactory(),
    "FORCE": _ForceExternalFactory(),
    "SET SCHEMA": _SetSchemaFactory(),
    "GET SCHEMA": _GetSchemaFactory(),
    "CLEAR CACHE": _ClearCacheFactory(),
    "SET": _SetParameterFactory(),
    "CANCEL": _CancelQueryFactory(),
    "KILL": _KillQueryFactory(),
    "GET SYSTEM METADATA": _GetSystemMetadataFactory(),
}
"""Mapping from query type to its request factory"""


def _convert_exception(msg: proto.ConfirmationResponse) -> SQLException:
    """Internal routine to convert the google protobuf ConfirmationResponse
    to an exception
    """
    if msg.type not in [proto.ConfirmationResponse.RESPONSE_WARN, proto.ConfirmationResponse.RESPONSE_ERROR]:
        raise IOError("Invalid message received")

    if msg.vendor_code < 0:
        return Error(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)

    return Warning(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)


def _send_msg(conn: "Connection", protobuf_msg: Message) -> None:
    """Internal routine to send a protobuf message on a connection"""
    if not conn.sock:
        raise ProgrammingError("Connection not available")

    logger.debug("Sending message on socket %s: %s", conn.sock, protobuf_msg)

    try:
        conn.sock.sendall(struct.pack("!i", protobuf_msg.ByteSize()) + protobuf_msg.SerializeToString())
    except IOError:
        raise IOError("Network send error")


def _recv_all(conn: "Connection", size: int) -> bytes:
    """Internal routine to receive `size` bytes of data from a connection"""
    if not conn.sock:
        raise Error("Connection not available")

    while len(conn._buffer) < size:
        received = conn.sock.recv(16777216)  # 16MB buffer
        if not received:
            raise IOError("Network receive error")
        conn._buffer.extend(received)

    ret = conn._buffer[:size]
    conn._buffer = conn._buffer[size:]

    return ret


def _recv_msg(conn: "Connection", protobuf_msg: _MsgT) -> _MsgT:
    """Internal routine to receive a protobuf message on a connection"""
    hdr = _recv_all(conn, 4)
    msgsize = _unpack_int(hdr)[0]

    if msgsize == proto.QUIESCE:
        raise Error(f"Server is quiescing")

    msg = _recv_all(conn, msgsize)

    protobuf_msg.ParseFromString(bytes(msg))

    logger.debug("Received message on connection %s: %s", conn.sock, protobuf_msg)

    return protobuf_msg


@dataclass(frozen=True)
class _PublicKey:
    """
    A class containing the values for a diffie hellman public key.

    Note that we don't do any validation of the prime (p) or the generator (g)
    because we get them from the database, and we assume the database knows what
    it is doing.
    """

    p: int
    g: int
    y: int


def _read_PEM(pemstr: str) -> _PublicKey:
    """
    Parse a PEM public key and return the values
    in our internal _PublicKey class

    Note that you can ask openssl to show you the
    internals of a PEM file by doing:
        openssl asn1parse -in my_pem_file -inform pem -i

    Which in the case of a DiffieHelman public key will
    produce
    0:d=0    hl=4 l= 548 cons: SEQUENCE
    4:d=1    hl=4 l= 279 cons:  SEQUENCE
    8:d=2    hl=2 l=   9 prim:   OBJECT            :dhKeyAgreement
    19:d=2   hl=4 l= 264 cons:   SEQUENCE
    23:d=3   hl=4 l= 257 prim:    INTEGER           :FFFFFFFFFFFFFFFFC90FDAA...
    284:d=3  hl=2 l=   1 prim:    INTEGER           :02
    287:d=1  hl=4 l= 261 prim:  BIT STRING

    """
    # Split the PEM into lines and throw away any empty lines
    lines = [line for line in pemstr.split("\n") if line]

    # We expect it to start with the magic strings. if not, just bail
    if lines[0] != "-----BEGIN PUBLIC KEY-----" or lines[-1] != "-----END PUBLIC KEY-----":
        raise OperationalError("Invalid PEM certificate received")

    # Rejoin the guts of the PEM file without the beginning and ending line
    pemstr = "".join(lines[1:-1])

    # Get the binary, base64 decoded version
    pembin = base64.b64decode(pemstr)

    # Now start ASN.1 parsing of the PEM binary
    decoder = asn1.Decoder()
    decoder.start(pembin)
    decoder.enter()
    decoder.enter()
    _, keytype = decoder.read()

    # This magic string is defined in the internet standards for
    # "dhKeyAgreement" key type (google it)
    if keytype != _OID_RSA_DH:
        raise OperationalError(f"Invalid public key type {keytype} received")

    decoder.enter()
    _, p = decoder.read()  # prime value
    _, g = decoder.read()  # generator value
    decoder.leave()
    decoder.leave()
    _, value = decoder.read()
    decoder.start(value)
    _, y = decoder.read()  # public key Y value

    return _PublicKey(p, g, y)


def _write_PEM(public_key: _PublicKey) -> str:
    """
    Given one of our internal public key objects, generate
    a PEM file representation
    """
    encoder = asn1.Encoder()
    encoder.start()
    encoder.write(public_key.y, asn1.Numbers.Integer)
    binary_key = encoder.output()

    encoder.start()
    with encoder.construct(asn1.Numbers.Sequence):
        with encoder.construct(asn1.Numbers.Sequence):
            encoder.write(_OID_RSA_DH, asn1.Numbers.ObjectIdentifier)
            with encoder.construct(asn1.Numbers.Sequence):
                encoder.write(public_key.p, asn1.Numbers.Integer)
                encoder.write(public_key.g, asn1.Numbers.Integer)
        encoder.write(binary_key, asn1.Numbers.BitString)

    # Generate the output and base64 encode it
    final_bytes = base64.b64encode(encoder.output()).decode()

    # split it into 64 character chunks
    final_bytes = "\n".join([final_bytes[i : i + 64] for i in range(0, len(final_bytes), 64)])

    # Throw the magic strings at the beginning and end
    return "-----BEGIN PUBLIC KEY-----\n" + final_bytes + "\n-----END PUBLIC KEY-----\n"


def Date(year: int, month: int, day: int) -> datetime.datetime:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Date object from year, month, day
    """
    return datetime.datetime(year, month, day)


def Time(hour: int, minute: int, second: int) -> datetime.time:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Time object from hour, minute, second
    """
    return datetime.time(hour, minute, second)


def Timestamp(year: int, month: int, day: int, hour: int, minute: int, second: int) -> float:  # pylint: disable=invalid-name,too-many-arguments
    """Type constructor required in PEP 249 to construct
    a Timestamp object from year, month, day, hour, minute, second
    """
    return datetime.datetime(year, month, day, hour, minute, second).timestamp()


def DateFromTicks(ticks: float) -> datetime.datetime:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Date object from a timestamp of seconds since epoch
    """
    return datetime.datetime.utcfromtimestamp(ticks)


def TimeFromTicks(ticks: float) -> datetime.time:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Time object from a timestamp of seconds since epoch
    """
    date_time = datetime.datetime.utcfromtimestamp(ticks)
    return datetime.time(date_time.hour, date_time.minute, date_time.second)


def TimestampFromTicks(ticks: float) -> float:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Timestamp object from a timestamp of seconds since epoch
    """
    return ticks


def _hash_key(shared_key: bytes, salt: bytes) -> bytes:
    """Internal key hash function"""
    # No idea where this algorithm came from, but do a home grown key
    # derivation function
    buffer = struct.pack("!i", len(shared_key))
    buffer = buffer + salt
    buffer = buffer + shared_key
    return hashlib.sha256(buffer).digest()


# Sessions code

# Used for representing a session created with a security token sign in


@dataclass
class SecurityToken:
    """A security token that can be retrieved from a connection object using the
    attribute `security_token` and may be used on subsequent connection calls
    """

    token_data: str
    token_signature: str
    issuer_fingerprint: str

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> SecurityToken:
        return SecurityToken(json_dct["token_data"], json_dct["token_signature"], json_dct["issuer_fingerprint"])


TLSArgType = Literal[1, "off", 2, "unverified", 3, "on"]


def is_tls_arg_type(o: object) -> TypeGuard[TLSArgType]:
    return o in typing.get_args(TLSArgType)


HandshakeArgType = Literal[2, "gcm", "", 3, "sso"]


def is_handshake_arg_type(o: object) -> TypeGuard[HandshakeArgType]:
    return o in typing.get_args(HandshakeArgType)


class Connection:
    """A connection to the Ocient Hyperscale Data Warehouse. Normally constructed by
    calling the module `connect()` call, but can be constructed
    directly
    """

    # pylint: disable=too-many-instance-attributes
    TLS_NONE: Final = 1  # : :meta private:
    TLS_UNVERIFIED: Final = 2  # : :meta private:
    TLS_ON: Final = 3  # : :meta private:

    HANDSHAKE_GCM: Final = 2
    HANDSHAKE_SSO: Final = 3

    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 4050
    DEFAULT_DATABASE = "system"

    # This setting is for test environments only.  It turns off SSL certificate verification
    # for SSO authentication servers, which is never something you would want to do
    # in production, however in test environments it can be useful
    SSO_SERVER_CERTIFICATE_VERIFICATION = True

    hosts: List[str] = []
    port: Optional[int] = None
    database: str
    tls: Optional[Literal[1, 2, 3]] = None
    force: Optional[bool] = None
    handshake: Optional[Literal[2, 3]] = None
    identity_provider: Optional[str] = None
    secondary_interfaces: Optional[List[List[Tuple[str, int]]]] = None
    secondary_index = -1
    sock: Optional[Union[socket.socket, ssl.SSLSocket]] = None
    session_id = str(uuid.uuid1())
    performance_mode = proto.OFF

    server_version: Tuple[int, int, int] = (0, 0, 0)

    security_token: Optional[SecurityToken] = None
    serverSessionId: Optional[str] = None

    schema: Optional[str] = None
    service_class: Optional[str] = None

    # Whether the next execute query run on this connection will be redirected. Does nothing if force is set to true
    force_next_redirect = False

    # The current cursor
    _current_cursor: Optional[Cursor] = None

    # The timeout set on the connect call
    timeout: Optional[float] = None

    # The timeout set on the SSO authorization call
    # sso_timeout: Optional[float] = None

    # Sessions code end

    # the PEP 249 standard recommends making the module level exceptions
    # also attributes on the Connection class
    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    InternalError = InternalError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    IntegrityError = IntegrityError
    DataError = DataError
    NotSupportedError = NotSupportedError

    # Set the SSL Certificate verification for SSO servers setting
    @classmethod
    def set_sso_server_certificate_verification(cls, value: bool) -> None:
        cls.SSO_SERVER_CERTIFICATE_VERIFICATION = value

    def _sslize_connection(self) -> None:
        """
        If SSL is specified, wrap the Connection's socket in an SSL connection
        """
        if self.tls != self.TLS_NONE:
            assert self.sock is not None
            logger.debug("Creating TLS connection")
            context = ssl.create_default_context()
            context.check_hostname = False
            if self.tls != self.TLS_ON:
                context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(self.sock)

    # Note that there are a couple of places in the code where we reconstruct the Connection.  If you add a parameter here, make sure to update those
    # places
    def __init__(
        self,
        dsn: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        database: Optional[str] = None,
        tls: Optional[TLSArgType] = None,
        handshake: Optional[HandshakeArgType] = None,
        force: Optional[bool] = None,
        configfile: Optional[str] = None,
        security_token: Optional[SecurityToken] = None,
        performance_mode: int = proto.OFF,
        sso_callback_url: Optional[str] = None,
        sso_code: Optional[str] = None,
        sso_state: Optional[str] = None,
        sso_redirect_state: Optional[Dict[Any, Any]] = None,
        sso_oauth_flow: str = "",
        sso_timeout: float = SSO_RESPONSE_TIMEOUT,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Connection objects should be created by calling the `connect()` api. See
        that api documentation for description of parameters.

        See the connect() function for a description of the paramters
        """
        # pylint: disable=too-many-arguments,no-member
        # pylint: disable=no-member
        user, password = self._parse_args(
            dsn, user, password, host, database, tls, handshake, force, configfile, timeout
        )
        assert self.port is not None
        assert self.force is not None

        self.performance_mode = performance_mode

        # Actually make the connection
        self.reconnect(
            user,
            password,
            security_token,
            sso_callback_url,
            sso_code,
            sso_state,
            sso_redirect_state,
            sso_oauth_flow,
            sso_timeout,
        )

    def reconnect(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[SecurityToken] = None,
        sso_callback_url: Optional[str] = None,
        sso_code: Optional[str] = None,
        sso_state: Optional[str] = None,
        sso_redirect_state: Optional[Dict[Any, Any]] = None,
        sso_oauth_flow: str = "",
        sso_timeout: float = SSO_RESPONSE_TIMEOUT,
    ) -> None:
        """
        Make a connection.  Called either from the Connection init method,
        or when we are being redirected.
        """

        assert self.port is not None

        saved_exc: Optional[Exception] = None
        for one_host in self.hosts:
            try:
                logger.debug("Trying to connect to %s:%s", one_host, self.port)
                self.sock = socket.create_connection((one_host, self.port))
                self._set_socket_options(self.sock)
                logger.debug("Connected to %s: %s on socket %s", one_host, self.port, self.sock)
                saved_exc = None
                break
            except ConnectionError as exc:
                saved_exc = exc
            except Exception as exc:
                saved_exc = exc

        if saved_exc is not None:
            raise Error(
                reason=f"Unable to connect to {','.join(self.hosts)}:{self.port}: {str(saved_exc)}",
                sql_state="08001",
                vendor_code=-201,
            ) from saved_exc

        self._sslize_connection()

        if self.timeout is not None and self.sock is not None:
            self.sock.settimeout(self.timeout)

        self._buffer: bytearray = bytearray()
        self.security_token = security_token
        if self.security_token is not None:
            self._client_handshake_security_token()
            return

        # We are being constructed after getting an SSO authentication flow
        # response. We have to turn the "code" into a full blown token
        if sso_code:
            user, password = sso.sso_get_credentials_from_code(sso_code, sso_state, sso_redirect_state)

        # If we are doing SSO, but are only given the database, get the authenticators and
        # raise SSORedirection exception
        if self.handshake == self.HANDSHAKE_SSO and not user and not password and self.database:
            authenticators = self._get_authenticators(self.database)

            user, password = sso.sso_get_credentials(
                authenticators, sso_oauth_flow, sso_callback_url, sso_timeout, self.identity_provider
            )

        # this is the "normal" (e.g. non-SSO userid/password) flow
        assert self.force is not None

        self._client_handshake_GCM(
            user=user, password=password, is_explicit_sso=(self.handshake == self.HANDSHAKE_SSO), force=self.force
        )

    def __enter__(self) -> "Connection":
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    def _initialize_client_connection(
        self,
        client_connection_message: Union[
            proto.ClientConnection,
            proto.ClientConnectionGCM,
            proto.ClientConnectionSecurityToken,
            proto.ClientConnectionSSO,
        ],
    ) -> None:
        """Initializes fields used in initial client handshake requests.
        1. database
        2. clientid (pyocient)
        3. protocol version
        4. version_major
        5. version_minor
        6. session id

        Note, not all fields are initialized. Some fields are special to certain client handshakes.
        For example, the SSO handshake with token does not take user and instead takes a security token.

        Args:
            client_connection_message ([proto message]): the client handshake request to initialize
        """
        assert self.database is not None
        client_connection_message.database = self.database
        client_connection_message.clientid = DRIVER_ID
        client_connection_message.version = PROTOCOL_VERSION
        client_connection_message.majorClientVersion = version_major
        client_connection_message.minorClientVersion = version_minor
        client_connection_message.patchClientVersion = version_patch
        client_connection_message.sessionID = self.session_id

    def _client_handshake_GCM(
        self, user: Optional[str], password: Optional[str], is_explicit_sso: bool = False, force: bool = False
    ) -> None:
        while True:
            ##################################################################
            # Send the CLIENT_CONNECTION request
            ##################################################################
            client_connection: Union[proto.ClientConnection, proto.ClientConnectionGCM]
            req = proto.Request()
            req.type = req.CLIENT_CONNECTION_GCM
            client_connection = req.client_connection_gcm
            client_connection.explicitSSO = is_explicit_sso
            if user is not None:
                client_connection.userid = user
            if self.identity_provider is not None:
                client_connection.identityProvider = self.identity_provider
            self._initialize_client_connection(client_connection)

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            rsp1: Union[proto.ClientConnectionResponse, proto.ClientConnectionGCMResponse]
            # GCM or explicit SSO
            rsp1 = _recv_msg(self, proto.ClientConnectionGCMResponse())

            if rsp1.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(Warning(rsp1.response.reason, rsp1.response.sql_state, rsp1.response.vendor_code))
            elif not rsp1.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                raise _convert_exception(rsp1.response)

            (cipher, generated_hmac, public_key) = self._encryption_routine(password, rsp1.iv, rsp1.pubKey)

            pem_public_key = _write_PEM(public_key)

            ##################################################################
            # Send the CLIENT_CONNECTION2 request
            ##################################################################
            req = proto.Request()
            req.type = req.CLIENT_CONNECTION_GCM2
            req.client_connection_gcm2.cipher = cipher
            req.client_connection_gcm2.force = force
            req.client_connection_gcm2.hmac = generated_hmac
            req.client_connection_gcm2.explicitSSO = is_explicit_sso
            req.client_connection_gcm2.pubKey = pem_public_key

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            rsp2: Union[proto.ClientConnection2Response, proto.ClientConnectionGCM2Response]
            # GCM or explicit SSO
            rsp2 = _recv_msg(self, proto.ClientConnectionGCM2Response())

            if rsp2.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(Warning(rsp2.response.reason, rsp2.response.sql_state, rsp2.response.vendor_code))

            if rsp2.response.type != proto.ConfirmationResponse.RESPONSE_ERROR:
                # Save the server session id
                self.serverSessionId = rsp2.serverSessionId
                received_token = rsp2.securityToken
                self.security_token = SecurityToken(
                    received_token.data, received_token.signature, received_token.issuerFingerprint
                )
                logger.debug("Connected to server session Id: %s", self.serverSessionId)
                # Save secondary interfaces.
                self._save_secondary_interfaces(rsp2.secondary)

                if rsp2.HasField("serverVersion"):
                    self.server_version = (
                        rsp2.serverVersion.majorServerVersion,
                        rsp2.serverVersion.minorServerVersion,
                        rsp2.serverVersion.patchServerVersion,
                    )

                # Redirect the connection
                if rsp2.redirect:
                    assert self.sock is not None
                    self.sock.close()
                    mapped_host, mapped_port = self.resolve_new_endpoint(rsp2.redirectHost, rsp2.redirectPort)
                    logger.debug(
                        "Redirecting connection to %s:%s, which maps to %s:%s",
                        rsp2.redirectHost,
                        rsp2.redirectPort,
                        mapped_host,
                        mapped_port,
                    )
                    self.sock = socket.create_connection((mapped_host, mapped_port))
                    self._set_socket_options(self.sock)
                    logger.debug("Connected to %s:%s on socket %s", mapped_host, mapped_port, self.sock)
                    self._sslize_connection()

                    return self._client_handshake_GCM(
                        user=user, password=password, is_explicit_sso=is_explicit_sso, force=force
                    )

                break

            # there is something broken in our handshake...retry
            if rsp2.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp2.response)

    def _client_handshake_security_token(self, force: bool = False) -> None:
        """Once a connection acquires a security token, it can use that to log in. This handshake only
        sends 1 message whereas the other handshakes send 2. self.security_token must be set.
        """
        while True:
            req = proto.Request()
            req.type = req.CLIENT_CONNECTION_SECURITY_TOKEN
            client_connection = req.client_connection_security_token

            self._initialize_client_connection(client_connection)
            # Attach the security token used to log in
            assert self.security_token is not None
            client_connection.securityToken = self.security_token.token_data
            client_connection.tokenSignature = self.security_token.token_signature
            client_connection.issuerFingerprint = self.security_token.issuer_fingerprint
            client_connection.force = force

            _send_msg(self, req)

            rsp = _recv_msg(self, proto.ClientConnectionSecurityTokenResponse())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(Warning(rsp.response.reason, rsp.response.sql_state, rsp.response.vendor_code))
            elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                # Save secondary interfaces.
                self._save_secondary_interfaces(rsp.secondary)
                # Redirect the connection if requested
                if rsp.redirect:
                    assert self.sock is not None
                    self.sock.close()
                    mapped_host, mapped_port = self.resolve_new_endpoint(rsp.redirectHost, rsp.redirectPort)
                    logger.debug(
                        "Redirecting connection to %s:%s, which maps to %s:%s",
                        rsp.redirectHost,
                        rsp.redirectPort,
                        mapped_host,
                        mapped_port,
                    )
                    self.sock = socket.create_connection((mapped_host, mapped_port))
                    self._set_socket_options(self.sock)
                    logger.debug(f"Connected to {mapped_host}:{mapped_port} on socket {self.sock}")
                    self._sslize_connection()

                    return self._client_handshake_security_token(True)

                # Capture the session id
                self.serverSessionId = rsp.serverSessionId
                logger.debug(f"Connected to server session Id: {self.serverSessionId}")
                break
            # there is something broken in our handshake...retry
            if rsp.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp.response)

    def _set_socket_options(self, sock: socket.socket) -> None:
        """
        Awkwardly socket options are platform specific.  Set
        TCP socket options to keep connections alive
        """
        plat = platform.system()
        if plat == "Linux":
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
        if plat == "Darwin":
            TCP_KEEPALIVE = 0x10
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 3)
        if plat == "Windows":
            sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10 * 1000, 3 * 1000))

    def _save_secondary_interfaces(
        self, new_secondary_interfaces: RepeatedCompositeFieldContainer[proto.SecondaryInterfaceList]
    ) -> None:
        """After secondary interfaces are sent from the server, we need to
        save them and use them for redirecting. This is important if we
        get redirected to mapped sql endpoints.

        Args:
            secondary_interfaces:
            the secondary interfaces, which is really a list of list of strings.
        """
        self.secondary_interfaces = []
        for i in range(len(new_secondary_interfaces)):
            self.secondary_interfaces.append([])
            for j in range(len(new_secondary_interfaces[i].address)):
                interface = new_secondary_interfaces[i].address[j]
                (interface_ip, interface_port) = interface.split(":")
                # Return of gethostbyname_ex is (hostname, alias of host name, other ip addresses of host name)
                try:
                    other_ips = socket.gethostbyname_ex(interface_ip)[2]
                    for other_ip in other_ips:
                        self.secondary_interfaces[i].append((other_ip, int(interface_port)))
                except socket.gaierror:
                    pass

        hosts: List[Tuple[str, int]] = []
        assert self.port is not None
        for one_host in self.hosts:
            try:
                hosts = hosts + [(host, self.port) for host in socket.gethostbyname_ex(one_host)[2]]
            except socket.gaierror:
                pass
        for outer_list in self.secondary_interfaces:
            for index in range(len(outer_list)):
                if outer_list[index] in hosts:
                    self.secondary_index = index
                    break

        logger.debug(
            "Saving secondary interfaces: index %s interfaces %s", self.secondary_index, self.secondary_interfaces
        )

    def _encryption_routine(
        self, password: Optional[str], initialization_vector: bytes, pem_peer_key: str
    ) -> Tuple[bytes, bytes, _PublicKey]:
        """Internal routine to do the encryption handshake of
        the password
        """

        if password is None:
            raise Error("Missing password")

        peer_key = _read_PEM(pem_peer_key)

        # Generate a random secret
        my_secret = int(binascii.hexlify(os.urandom(32)), base=16)

        # Our public version of this secret is g^secret mod p
        my_public = pow(peer_key.g, my_secret, peer_key.p)

        # Create a shared key by using our secret and the peer's public value
        #  peer ^ secret mod p
        shared_key = pow(peer_key.y, my_secret, peer_key.p).to_bytes(256, byteorder="big")

        key = _hash_key(shared_key, b"\0")
        mac_key = _hash_key(shared_key, b"\1")

        # This is the only remaining use of the cryptography library.  I would like to remove it
        # if I could find a decent AES encryption library
        encryptor = Cipher(algorithms.AES(key), modes.GCM(initialization_vector)).encryptor()
        # We do not use AAD
        cipher = encryptor.update(password.encode(encoding="UTF-8", errors="strict")) + encryptor.finalize()
        # Server side expects that the tag is at the end of the cipher text.
        cipher += encryptor.tag

        # Now create an HMAC using the other KDF derived key and the
        # encrypted password
        generated_hmac = hmac.HMAC(mac_key, cipher, digestmod=hashlib.sha256).digest()

        return (cipher, generated_hmac, _PublicKey(peer_key.p, peer_key.g, my_public))

    def _parse_args(
        self,
        dsn: Optional[str],
        user: Optional[str],
        password: Optional[str],
        host: Optional[str],
        database: Optional[str],
        tls: Optional[TLSArgType],
        handshake: Optional[HandshakeArgType],
        force: Optional[bool],
        configfile: Optional[str],
        timeout: Optional[float],
    ) -> Tuple[Optional[str], Optional[str]]:  # pylint: disable=too-many-arguments
        """Internal routine to resolve function arguments, config file, and dsn"""
        # pylint: disable=no-member,too-many-branches,too-many-statements
        # First, parse the DSN if it exists and store the values in the dsnparams dictionary
        dsnparams = {}
        if dsn is not None:
            parsed = dsnparse.parse(dsn)

            if parsed.scheme and parsed.scheme.lower() != "ocient":
                raise MalformedURL(f"Invalid DSN scheme: {parsed.scheme}")

            dsnparams = {attr: getattr(parsed, attr) for attr in ["database", "user", "password", "port"]}

            if parsed.host:
                dsnparams["hosts"] = parsed.host.split(",")

            if "database" in dsnparams:
                if len(dsnparams["database"]) == 0:
                    del dsnparams["database"]
                elif dsnparams["database"].startswith("/"):
                    dsnparams["database"] = dsnparams["database"][1:]

            if "tls" in parsed.query:
                dsnparams["tls"] = parsed.query["tls"]

            if "force" in parsed.query:
                shouldForce = parsed.query["force"]
                if shouldForce.upper() == "TRUE":
                    dsnparams["force"] = True
                elif shouldForce.upper() == "FALSE":
                    dsnparams["force"] = False
                else:
                    raise MalformedURL(f"Invalid force string: {shouldForce}")

            if "handshake" in parsed.query:
                dsnparams["handshake"] = parsed.query["handshake"].lower()

            if "identityprovider" in parsed.query:
                dsnparams["identityprovider"] = parsed.query["identityprovider"].lower()

            if "logfile" in parsed.query:
                logger.addHandler(logging.FileHandler(filename=parsed.query["logfile"], encoding="utf-8"))

            if "loglevel" in parsed.query:
                loglevel = getattr(logging, parsed.query["loglevel"].upper(), None)
                if loglevel is not None:
                    logger.setLevel(loglevel)

            if "timeout" in parsed.query:
                dsnparams["timeout"] = float(parsed.query["timeout"])

            dsnparams = {k: v for k, v in dsnparams.items() if v is not None}

        connectparams: Mapping[str, object] = {
            "user": user,
            "password": password,
            "database": database,
            "tls": tls,
            "handshake": handshake,
            "force": force,
            "timeout": timeout,
        }

        connectparams = {k: v for k, v in connectparams.items() if v is not None}

        if host:
            # Handle host:port
            parts = host.split(":")
            if len(parts) == 1:
                connectparams["hosts"] = parts[0].split(",")
            elif len(parts) == 2:
                connectparams["hosts"] = parts[0].split(",")
                connectparams["port"] = int(parts[1])
            else:
                raise MalformedURL(f"Invalid host value: {host}")

        # Now build a configparser with default values
        config = configparser.ConfigParser(
            defaults={
                "port": str(self.DEFAULT_PORT),
                "database": self.DEFAULT_DATABASE,
                "tls": "unverified",
                "force": "false",
                "handshake": "",
            },
            interpolation=None,
        )
        configvals = None

        # If we have a config file try loading that
        if configfile is not None:
            config.read(configfile)

            lookup_host = dsnparams.get("hosts", None) or connectparams.get("hosts", None) or [self.DEFAULT_HOST]

            # Work out the host/database if we know it
            host_db = ",".join(lookup_host)  # type: ignore[arg-type]
            if database is not None:
                host_db = host_db + "/" + database

            # Try and match each section in the INI file with the host/database
            for s in config.sections():
                if re.match(s, host_db):
                    configvals = config[s]
                    break

        # if we didn't find a matching host (or there is no file). use the defaults
        if configvals is None:
            configvals = config["DEFAULT"]

        configparams: MutableMapping[str, object] = dict(configvals)

        connectparams = {k: v for k, v in connectparams.items() if v != ""}

        if isinstance(configparams["force"], str) and configparams["force"].upper() == "TRUE":
            configparams["force"] = True
        else:
            configparams["force"] = False

        defaultparams = {
            "user": None,
            "password": None,
            "hosts": [self.DEFAULT_HOST],
            "identityprovider": None,
            "timeout": None,
        }

        # This will merge the values we get from the config file with
        # the values from the DSN, with the values explicitly passed in
        # as parameters to this function
        params: MutableMapping[str, Any] = {**defaultparams, **configparams, **dsnparams, **connectparams}

        # And finally tidy up some things
        if isinstance(params["port"], str):
            params["port"] = int(params["port"])

        if isinstance(params["tls"], str):
            if params["tls"].lower() == "off":
                params["tls"] = self.TLS_NONE
            elif params["tls"].lower() == "unverified":
                params["tls"] = self.TLS_UNVERIFIED
            elif params["tls"].lower() == "on":
                params["tls"] = self.TLS_ON
            else:
                raise MalformedURL(f"Invalid tls value: {params['tls']}")
        elif isinstance(params["tls"], list):
            raise MalformedURL(f"Multiple TLS values detected: {params['tls']}")

        if isinstance(params["handshake"], str):
            if params["handshake"].lower() == "sso":
                params["handshake"] = self.HANDSHAKE_SSO
            # If they didn't specify handshake, it will be blank and thus should be GCM.
            elif params["handshake"].lower() == "gcm" or params["handshake"].lower() == "":
                params["handshake"] = self.HANDSHAKE_GCM
            else:
                raise MalformedURL(f"Invalid handshake value: {params['handshake']}")

        # Set our parameters, except for user and password
        for attr in ["database", "hosts", "port", "tls", "force", "handshake", "identityprovider", "timeout"]:
            setattr(self, attr, params[attr])

        # return the user and password as return values
        return params["user"], params["password"]

    def close(self) -> None:
        """Close the connection. Subsequent queries on this connection
        will fail
        """
        if not self.sock:
            raise Error("No connection")

        try:
            # Send end session message
            req = proto.Request()
            req.type = req.CLOSE_CONNECTION
            req.close_connection.endSession = True
            _send_msg(self, req)
        except IOError:
            # Ignore end session errors
            pass
        finally:
            logger.debug("Closing connection on socket %s", self.sock)
            # Do this little dance so that even if the close() call
            # blows up, we have already set self.sock to None
            sock = self.sock
            self.sock = None
            sock.close()

    def commit(self) -> None:
        """Commit a transaction. Currently ignored"""

    def cursor(self) -> "Cursor":
        """Return a new cursor for this connection"""
        if not self.sock:
            raise Error("No connection")

        if self._current_cursor is not None:
            self._current_cursor.close()

        self._current_cursor = Cursor(self)
        return self._current_cursor

    def __del__(self) -> None:
        if self.sock is not None:
            try:
                self.close()
            except Exception:
                pass

    def resolve_new_endpoint(self, new_host: str, new_port: int) -> Tuple[str, int]:
        """
        Handles mapping to a secondary interface based on the secondary interface mapping saved on this connection.

        Args:
            new_host[string]: the new host to be remapped
            new_port[int]: the new port to be remapped

        Returns:
            [tuple(string, int)]: The actual endpoint to connect to in the format: (host, port).
        """
        logger.debug(
            "Resolving new endpoint %s:%s with secondary_index %s and secondary_interface %s",
            new_host,
            new_port,
            self.secondary_index,
            self.secondary_interfaces,
        )

        new_endpoint = (new_host, new_port)
        endpoint_to_connect = None
        if self.secondary_index != -1:
            assert self.secondary_interfaces is not None
            outer_index = 0
            for outer_list in self.secondary_interfaces:
                if outer_list[0] == new_endpoint:
                    break
                outer_index += 1
            if outer_index < len(self.secondary_interfaces):
                endpoint_to_connect = self.secondary_interfaces[outer_index][self.secondary_index]
            else:
                endpoint_to_connect = new_endpoint

        else:
            endpoint_to_connect = new_endpoint

        logger.debug("Resolved new endpoint %s:%s to %s", new_host, new_port, endpoint_to_connect)

        return endpoint_to_connect

    def redirect(self, new_host: str, new_port: int) -> None:
        """
        Redirects to the proper secondary interface given a new endpoint.

        Args:
            new_host[string]: the new host to be remapped
            new_port[int]: the new port to be remapped

        Returns:
            [Connection]: A new connection.
        """
        remapped_host, remapped_port = self.resolve_new_endpoint(new_host, new_port)
        logger.debug(
            "Redirecting connection to %s:%s, which maps to %s:%s", new_host, new_port, remapped_host, remapped_port
        )

        self.close()

        self.host = [remapped_host]
        self.port = remapped_port

        self.reconnect(security_token=self.security_token)

    def refresh_token(self) -> None:
        """
        Used to refresh the token associated with a session
        """
        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_REFRESH_TOKEN
        assert self.security_token
        req.client_connection_refresh_token.oldSecurityToken.data = self.security_token.token_data
        req.client_connection_refresh_token.oldSecurityToken.signature = self.security_token.token_signature
        req.client_connection_refresh_token.oldSecurityToken.issuerFingerprint = self.security_token.issuer_fingerprint

        # Send message
        _send_msg(self, req)
        # Receive message
        rsp = _recv_msg(self, proto.ClientConnectionRefreshTokenResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(Warning(rsp.response.reason, rsp.response.sql_state, rsp.response.vendor_code))
        elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            # Capture the session id
            received_token = rsp.newSecurityToken
            self.security_token = SecurityToken(
                received_token.data, received_token.signature, received_token.issuerFingerprint
            )
            self._client_handshake_security_token()
            return

        # Something bad happened with the refresh attempt.
        raise _convert_exception(rsp.response)

    def refresh(self) -> None:
        """
        Used to refresh the session associated with this connection. The server will
        return a new server session id and security token.
        """
        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_REFRESH_SESSION

        # Send message
        _send_msg(self, req)
        # Receive message
        rsp = _recv_msg(self, proto.ClientConnectionRefreshSessionResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(Warning(rsp.response.reason, rsp.response.sql_state, rsp.response.vendor_code))
        elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            # Capture the session id
            self.serverSessionId = rsp.sessionInfo.serverSessionId
            logger.debug("Connected to server session Id: %s", self.serverSessionId)
            received_token = rsp.sessionInfo.securityToken
            self.security_token = SecurityToken(
                received_token.data, received_token.signature, received_token.issuerFingerprint
            )
            return
        elif rsp.response.vendor_code == SESSION_EXPIRED_CODE:
            self.refresh_token()
            return

        # Something bad happened with the refresh attempt.
        raise _convert_exception(rsp.response)

    def _get_authenticators(self, database: str) -> Any:
        """
        Fetch a list of SSO authenticators from the system, given a database name
        """
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("FETCH_AUTHENTICATORS")
        req.fetch_authenticators.database = database

        _send_msg(self, req)

        rsp = _recv_msg(self, proto.FetchAuthenticatorsResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(Warning(rsp.response.reason, rsp.response.sql_state, rsp.response.vendor_code))
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            pyocient_reason = f"Error when fetching authenticators for database {self.database}"

            # when tls is not enabled we get an empty response
            if not rsp.response.reason and not rsp.response.sql_state and not rsp.response.vendor_code:
                raise Error(pyocient_reason)

            # otherwise we get a legit SQL exception
            raise Error(
                reason=f"{rsp.response.reason} (Error when fetching authenticators for database {self.database})",
                sql_state=rsp.response.sql_state,
                vendor_code=rsp.response.vendor_code,
            )

        return rsp.authenticator


class Cursor:
    # pylint: disable=too-many-instance-attributes
    """A database cursor, which is used to manage a query and its returned results"""

    def __init__(self, conn: Connection) -> None:
        """Cursors are normally created by the cursor() call on a connection, but can
        be created directly by providing a connection
        """
        self.connection = conn
        self.arraysize = 1

        self._reinitialize()

    def __del__(self) -> None:
        if self.description:
            try:
                self._close_resultset()
            except Exception:
                pass

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    def _reinitialize(self) -> None:
        """Internal function to initialize a cursor"""
        # Set the state
        self.query_id = None
        self._rowcount = -1
        self.rownumber: Optional[int] = None
        self.resultset_tuple: Optional[Type[NamedTuple]] = None
        self.description: Optional[List[Tuple[str, int, None, None, None, None, None]]] = None
        self.end_of_data = False
        self.generated_result: Optional[str] = None
        self.list_result: Optional[List[NamedTuple]] = None
        self._buffers: List[bytes] = []
        self._offset = 0
        self._pending_ops: List[str] = []
        self.cols2Types: Dict[str, str] = {}
        self.colsPos: Dict[str, int] = {}
        self.messages: List[Tuple[Type[SQLException], SQLException]] = []

    def _check_response(self, rsp: proto.ConfirmationResponse) -> None:
        """
        Handle a confirmation response.  If it is OK just return, if it
        is a warning call warn, if it is an exception, raise.

        For warnings and exceptions, add to the messages list
        """
        if rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            return

        exc = _convert_exception(rsp)

        self.messages.append((type(exc), exc))

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            assert isinstance(exc, Warning)
            warn(exc)
        else:
            raise (exc)

    @property
    def rowcount(self) -> int:
        return self._rowcount

    def setinputsizes(self, sizes: Sequence[Optional[int]]) -> None:
        """This can be used before a call to .execute*() to predefine
        memory areas for the operation's parameters. Currently ignored
        """

    def setoutputsize(self, size: int, column: Optional[int] = None) -> None:
        """Set a column buffer size for fetches of large columns
        (e.g. LONGs, BLOBs, etc.). The column is specified as an
        index into the result sequence. Currently ignored
        """

    def close(self) -> None:
        """Close this cursor.  The current result set is closed, but
        the cursor can be reused for subsequent execute() calls.
        """
        if self.description:
            try:
                self._close_resultset()
            except Exception:
                pass

        self._reinitialize()

    def executemany(self, operation: str, parameterlist: Iterable[Any]) -> "Cursor":
        """Prepare a database operation (query or command) and then execute it against
        all parameter sequences or mappings found in the sequence parameterlist.

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)s

        An optional timeout can be provided as seconds.
        """
        self._reinitialize()

        # parameterlist should not be None, but some applications set it so.
        # Guard against that
        if parameterlist is None:
            parameterlist = {}

        # we can't just execute all the queries at once....ocient only allows
        # one query at a time on a connection.  So queue up all the queries and
        # we'll call them later
        for param in parameterlist:
            self._pending_ops.append(self._expand_parameters(operation, param))

        if self._pending_ops:
            self._execute_internal(self._pending_ops.pop(0))

        return self

    def execute(self, operation: str, parameters: Optional[Any] = NoParams) -> "Cursor":
        """Prepare and execute a database operation (query or command).

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)s

        Parameter expansion examples:
        - execute('SELECT * FROM empl WHERE id=%d', 13)
        - execute('SELECT * FROM empl WHERE id IN %s', ((5,6),))
        - execute('SELECT * FROM empl WHERE name=%s', 'John Doe')
        - execute('SELECT * FROM empl WHERE name LIKE %s', 'J%')
        - execute('SELECT * FROM empl WHERE name=%(name)s AND city=%(city)s', { 'name': 'John Doe', 'city': 'Nowhere' } )
        - execute('SELECT * FROM cust WHERE salesrep=%s AND id IN (%s)', ('John Doe', (1,2,3)))
        - execute('SELECT * FROM empl WHERE id IN %s', (tuple(range(4)),))
        - execute('SELECT * FROM empl WHERE id IN %s', (tuple([3,5,7,11]),))

        Because of parameter expansion, percent characters ('%') always need to be escaped ('%%') if
        the parameters argument is included
        """
        self._reinitialize()

        self._execute_internal(operation, parameters)

        return self

    @staticmethod
    def _decimal_str(value: decimal.Decimal) -> str:
        """
        This is NOT a good performer, but correctly converts python
        Decimals to ocient Decimals string in a non-lossy way
        """
        sign, digits, exp = value.as_tuple()

        digit_str = "".join([str(d) for d in digits])

        assert isinstance(exp, int)
        if exp < 0:
            digit_str = digit_str.rjust(-exp + 1, "0")
            digit_str = digit_str[:exp] + "." + digit_str[exp:]
        elif exp > 0:
            digit_str = digit_str + ("0" * exp)

        if sign:
            digit_str = "-" + digit_str

        return digit_str

    @staticmethod
    def _expand_parameter(value: Any) -> Any:
        """
        Convert python types to their SQL string equivalents
        """
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            if value:
                return "True"
            else:
                return "False"
        elif isinstance(value, str):
            v = value.replace("'", "''")
            return f"'{v}'"
        elif isinstance(value, datetime.datetime):
            return f"TIMESTAMP('{str(value)}')"
        elif isinstance(value, datetime.date):
            return f"DATE('{str(value)}')"
        elif isinstance(value, datetime.time):
            return f"TIME('{str(value)}')"
        elif isinstance(value, decimal.Decimal):
            return f"DECIMAL('{Cursor._decimal_str(value)}')"
        elif isinstance(value, bytes):
            return f"binary('0x{value.hex()}')"
        elif isinstance(value, list):
            return f"array[{','.join(str(Cursor._expand_parameter(p)) for p in value)}]"
        else:
            return value

    @staticmethod
    def _expand_parameters(operation: str, parameters: Optional[Any]) -> str:
        if parameters == NoParams:
            return operation

        # Guard against None in parameters
        if parameters is None:
            parameters = {}

        formatted_parameters: Optional[Any] = None

        if isinstance(parameters, tuple):
            formatted_parameters = tuple(Cursor._expand_parameter(v) for v in parameters)
        elif isinstance(parameters, list):
            formatted_parameters = [Cursor._expand_parameter(v) for v in parameters]
        elif isinstance(parameters, dict):
            formatted_parameters = {k: Cursor._expand_parameter(v) for k, v in parameters.items()}
        else:
            formatted_parameters = Cursor._expand_parameter(parameters)

        try:
            result = operation % formatted_parameters
        except ValueError as e:
            raise ProgrammingError(reason="Invalid statement. Ensure percent signs are correctly escaped") from e
        except TypeError as e:
            raise ProgrammingError(
                reason=f"Invalid parameter expansion. Types do not match parameters (statement '{operation}', parameters '{parameters}', paramters after SQL formatting '{formatted_parameters}')"
            ) from e

        return result

    def _execute_internal(self, operation: str, parameters: Optional[Any] = NoParams) -> None:
        """Internal execute routine that gets called from execute and executemany"""
        # pylint: disable=too-many-branches

        operation = Cursor._expand_parameters(operation, parameters)

        # We need to figure out whether we should call
        # execute_query or execute_update
        stripped = operation

        # Loop until we have some starting words. Note this
        # doesn't actually handle the case of 'word1 /* comment */ word2',
        # but none of the other clients do either...
        while True:
            # strip off starting spaces
            stripped = stripped.lstrip()

            # if this starts with --, strip the rest of the line
            if stripped.startswith("--"):
                pos = stripped.find("\n")
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos + 1 :]

            # if this starts with /*, strip until */
            elif stripped.startswith("/*"):
                pos = stripped.find("*/")
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos + 2 :]
            else:
                # yay, no comments, move to the next phase
                break

        # if we don't have anything left, just return []
        if not stripped:
            return

        # check for enclosing parens
        if stripped[0] == "(":
            stripped = stripped[1:]

        # now split out the words
        try:
            words = shlex.split(stripped)
            if len(words) > 4:
                words = words[:3] + [" ".join(words[3:])]
        except ValueError:
            # indicates unmatched quotes
            words = stripped.split(None, 3)

        # Single word matches
        query_type = words[0].upper()
        if query_type in ["SELECT", "WITH", "EXPORT", "CHECK", "SHOW", "PREVIEW"]:
            if len(words) > 1 and (words[1].upper() == "STATS" or words[1].upper() == "STATISTICS"):
                self._execute_update(operation)
            else:
                return self._execute_query(operation=operation, query_type=query_type)
        elif query_type in ["EXPLAIN"]:
            # explain pipeline
            if len(words) > 1 and words[1].upper() == "PIPELINE":
                return self._execute_query(operation=operation, query_type=query_type + " PIPELINE")
            else:
                return self._execute_query(operation=operation, query_type=query_type)
        elif query_type == "FORCE":
            self._execute_force(operation=operation)
        elif query_type == "SET":
            self._execute_set(words[1:])
        elif query_type == "GET":
            self._execute_get(words[1:])
        elif query_type == "KILL":
            if self.connection.server_version[0] >= 25:
                self._execute_update(operation)
            else:
                self._execute_cancelkill(query_type, words[1:])
        elif query_type == "CANCEL":
            if len(words) > 1 and words[1].upper() == "TASK":
                self._execute_update(operation)
            else:
                if self.connection.server_version[0] >= 25:
                    self._execute_update(operation)
                else:
                    self._execute_cancelkill(query_type, words[1:])
        elif query_type == "CLEAR":
            self._execute_clear(words[1:])
        elif query_type == "PERFORMANCE":
            self._execute_performance_mode(words[1:])
        elif query_type == "LIST":
            raise NotSupportedError(f"'{operation}' not supported by pyocient'")
        elif query_type == "DESCRIBE":
            return self._execute_describe(words[1:])

            # DESCRIBE was introduced in rolehostd in 25.X so prefer the server-side implementation if we can
            # system_version = self.getSystemVersion()
            # if system_version >= OcientVersion(25, X, 0):
            #     return self._execute_query(operation=operation, query_type=query_type)
            # else:
            #     return self._execute_describe(words[1:])
        else:
            # ok, this is an update
            self._execute_update(operation)

    def tables(self, schema: Optional[str] = None, table: str = "%") -> "Cursor":
        """Get the database tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TABLES, schema=schema or "", table=table)
        return self

    def system_tables(self, table: str = "%") -> "Cursor":
        """Get the database system tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_SYSTEM_TABLES, table=table)
        return self

    def views(self, schema: Optional[str] = None, view: str = "%") -> "Cursor":
        """Get the database views"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_VIEWS, schema=schema or "", view=view)
        return self

    def columns(self, schema: Optional[str] = None, table: str = "%", column: str = "%") -> "Cursor":
        """Get the database columns"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_COLUMNS, schema=schema or "", table=table, column=column)
        return self

    def indexes(self, schema: Optional[str] = None, table: str = "%") -> "Cursor":
        """Get the database indexes"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_INDEX_INFO, schema=schema or "", table=table)
        return self

    def getTypeInfo(self) -> "Cursor":  # pylint: disable=invalid-name
        """Get the database type info"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TYPE_INFO)
        return self

    def getSystemVersion(self) -> OcientVersion:
        res = self._execute_systemmetadata(proto.FetchSystemMetadata.GET_DATABASE_PRODUCT_VERSION)
        assert isinstance(res, str)
        return OcientVersion.from_string(res)

    def _metadata_req(
        self,
        reqtype: proto.FetchSystemMetadata.SystemMetadataCall,
        schema: Optional[str] = None,
        table: str = "%",
        column: str = "%",
        view: str = "%",
    ) -> None:
        """Internal function to get database metadata"""
        # pylint: disable=no-member,too-many-arguments
        self._reinitialize()
        # req.fetch_system_metadata.GET_TABLES
        req = proto.Request()
        req.type = req.FETCH_SYSTEM_METADATA
        req.fetch_system_metadata.call = reqtype
        req.fetch_system_metadata.schema = schema or ""
        req.fetch_system_metadata.table = table
        req.fetch_system_metadata.column = column
        req.fetch_system_metadata.view = view
        req.fetch_system_metadata.test = True

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchSystemMetadataResponse())

        if (
            rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
            and rsp.response.vendor_code == SESSION_EXPIRED_CODE
        ):
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            self._metadata_req(reqtype, schema=schema, table=table, column=column, view=view)
            return

        self._check_response(rsp.response)

        self._get_result_metadata()

        self.rownumber = 0
        for blob in rsp.result_set_val.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def _execute_describe(self, params: Sequence[str]) -> None:
        """Fetch columns from table"""
        # pylint: disable=no-member
        schema, table = params[1].split(".")
        self.columns(schema=schema, table=table)
        columns = []
        self.description = []
        # This will remove everything but column name and type. Not strictly neccesary, but achieves closer parity with JDBC
        for rows in self:
            columns.append([rows.COLUMN_NAME, rows.TYPE_NAME])
            self.description.append(("COLUMN_NAME", TypeCodes.STRING.value, None, None, None, None, None))
            self.description.append(("TYPE", TypeCodes.STRING.value, None, None, None, None, None))
        Row = namedtuple("Row", ("name", "type"))
        self.list_result = [Row._make(x) for x in columns]
        self._offset = 0
        self.end_of_data = False

    def _execute_query(self, operation: str, query_type: str = "SELECT") -> None:
        """Execute a query"""
        # pylint: disable=no-member

        factory = _OCIENT_REQUEST_FACTORIES.get(query_type.upper(), None)

        if factory is None:
            raise NotSupportedError(f"Query type '{query_type}' not supported by pyocient'")
        # generate the appropriate request
        req = factory.request(operation)

        # Loop while we retry redirects and reconnects
        while True:
            assert self.connection.force is not None
            if req.type == proto.Request.RequestType.Value("EXECUTE_QUERY"):
                req.execute_query.force = self.connection.force
                req.execute_query.performanceMode = self.connection.performance_mode
                req.execute_query.forceRedirect = self.connection.force_next_redirect
                self.connection.force_next_redirect = False
            elif req.type == proto.Request.RequestType.Value("EXECUTE_EXPLAIN"):
                req.execute_explain.force = self.connection.force
            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, factory.response())
            except TimeoutError as e:
                raise e
            except IOError as e:
                # remake our connection.
                self.connection.reconnect(security_token=self.connection.security_token)
                self._restore_settings()

                continue

            if (
                rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
                and rsp.response.vendor_code == SESSION_EXPIRED_CODE
            ):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                continue

            self._check_response(rsp.response)

            # see if we are being told to redirect
            redirect = getattr(rsp, "redirect", False)
            if not redirect:
                break

            # remake our connection
            self.connection.redirect(rsp.redirectHost, rsp.redirectPort)
            self._restore_settings()

        query_id = getattr(rsp, "queryId", None)
        if query_id is not None:
            self.query_id = query_id

        self.rownumber = 0

        if query_type in ["SELECT", "WITH", "SHOW", "PREVIEW", "DESCRIBE"]:
            self._get_result_metadata()

        elif query_type == "EXPORT":
            self.description = [
                ("export", TypeCodes.CHAR.value, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("export",))  # type: ignore[assignment, misc]
            self.generated_result = rsp.exportStatement
            if len(rsp.queryId) > 0:
                self.query_id = rsp.queryId
        elif query_type == "EXPLAIN":
            self.description = [
                ("explain", TypeCodes.CHAR.value, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("explain",))  # type: ignore[assignment, misc]
            self.generated_result = rsp.plan
            if len(rsp.queryId) > 0:
                self.query_id = rsp.queryId
        elif query_type == "EXPLAIN PIPELINE":
            self.description = [
                ("explain_pipeline", TypeCodes.CHAR.value, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("explain_pipeline",))  # type: ignore[assignment, misc]
            self.generated_result = rsp.pipelineStatement

    def _get_result_metadata(self) -> None:
        """Internal routine to get metadata for a result set"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_METADATA

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchMetadataResponse())

        self._check_response(rsp.response)

        cols = {}
        for key, value in rsp.cols2pos.items():
            cols[value] = key

        self.description = []
        self.cols2Types = rsp.cols2Types
        self.cols2Pos = rsp.cols2pos
        colnames = []
        for i in range(len(cols)):  # pylint: disable=consider-using-enumerate
            name = cols[i]
            # This tuple is defined in PEP 249
            self.description.append(
                (name, TypeCodes[rsp.cols2Types[name]].value, None, None, None, None, None)
            )  # display_size  # internal_size  # precision  # scale  # null_ok
            colnames.append(name)
        self.resultset_tuple = namedtuple("Row", colnames, rename=True)  # type: ignore[assignment, misc]

    def _execute_update(self, operation: str) -> None:
        """Execute an update statement"""
        # pylint: disable=no-member
        # While we are redirecting...

        # There is no resultset data from an update
        self.end_of_data = True

        while True:
            req = proto.Request()
            req.type = req.EXECUTE_UPDATE
            req.execute_update.sql = operation
            assert self.connection.force is not None
            req.execute_update.force = self.connection.force

            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, proto.ExecuteUpdateResponse())
            except TimeoutError as e:
                raise e
            except IOError:
                # remake our connection.
                self.connection.reconnect(security_token=self.connection.security_token)
                self._restore_settings()

                continue

            if (
                rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
                and rsp.response.vendor_code == SESSION_EXPIRED_CODE
            ):
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                continue

            self._check_response(rsp.response)

            # see if we are being told to redirect
            if not rsp.redirect:
                self._rowcount = max(rsp.updateRowCount, rsp.updateRowCountLong)
                self.query_id = rsp.queryId

                if self._pending_ops:
                    operation = self._pending_ops.pop(0)
                    continue
                else:
                    break

            # remake our connection
            self.connection.redirect(rsp.redirectHost, rsp.redirectPort)
            self._restore_settings()

    def _restore_settings(self) -> None:
        saved_end_of_data = self.end_of_data

        if self.connection.schema is not None:
            logger.debug("Restoring schema %s after reconnect", self.connection.schema)
            try:
                self._execute_set(["schema", self.connection.schema])
            except Exception as e:
                logger.error("Error restoring schema: %s", str(e))

        if self.connection.service_class is not None:
            logger.debug("Restoring service class %s after reconnect", self.connection.service_class)
            try:
                self._execute_set(["service_class", self.connection.service_class])
            except Exception as e:
                logger.error("Error restoring service_class: %s", str(e))

        self.end_of_data = saved_end_of_data

    def _execute_force(self, operation: str) -> None:
        if operation.strip().upper() == "FORCE REDIRECT":
            # Sets the next command that is execute query to redirect
            self.connection.force_next_redirect = True
            self.end_of_data = True
        else:
            # Force external command
            self._execute_force_external(operation)

    def _execute_force_external(self, operation: str) -> None:
        # pylint: disable=no-member
        # While we are redirecting...
        factory = _OCIENT_REQUEST_FACTORIES["FORCE"]
        req = factory.request(operation=operation)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        self._check_response(rsp)

    def _execute_set(self, params: Sequence[str]) -> None:
        if len(params) != 2:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        op = params[0].upper()
        val: Union[int, str, float]
        val = params[1].strip()

        factory: Union[_SetSchemaFactory, _SetParameterFactory]
        if op == "SCHEMA":
            factory = _SetSchemaFactory()
            req = factory.request(val)
        elif op == "SERVICECLASS":  # Service Classes take string parameters, not int
            factory = _SetParameterFactory()
            req = factory.request(op, val)
        elif op in ["ADJUSTFACTOR", "PRIORITY"]:
            if val.lower() != "reset":
                try:
                    val = float(val)
                except ValueError:
                    raise ProgrammingError(reason="Syntax error in SET. Value must be numeric or 'reset'")
            factory = _SetParameterFactory()
            req = factory.request(op, val)
        else:
            if val.lower() != "reset":
                try:
                    val = int(val)
                except ValueError:
                    raise ProgrammingError(reason="Syntax error in SET. Value must be numeric or 'reset'")
            factory = _SetParameterFactory()
            req = factory.request(op, val)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_ERROR and rsp.vendor_code == SESSION_EXPIRED_CODE:
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            self._execute_set(params)
            return

        self._check_response(rsp)

        if op == "SCHEMA":
            self.connection.schema = str(val)
        elif op == "SERVICECLASS":
            self.connection.service_class = str(val)

    def _execute_get_schema(self) -> None:
        factory = _GetSchemaFactory()
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if (
            rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
            and rsp.response.vendor_code == SESSION_EXPIRED_CODE
        ):
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            self._execute_get_schema()
            return

        self._check_response(rsp.response)

        self.description = [
            ("schema", TypeCodes.CHAR.value, None, None, None, None, None)
        ]  # display_size  # internal_size  # precision  # scale  # null_ok

        Row = namedtuple("Row", ("schema",))
        self.list_result = [Row._make((rsp.schema,))]

    def _execute_performance_mode(self, params: Sequence[str]) -> None:
        if len(params) != 1:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        mode = params[0].upper()
        if mode == "OFF":
            self.connection.performance_mode = proto.OFF
        elif mode == "NETWORK":
            raise Error("PERFORMANCE NETWORK is not implemented")
        elif mode == "DATABASE":
            self.connection.performance_mode = proto.ROOT_OP_INST_DISCARD
        else:
            raise ProgrammingError(reason="Syntax error")

    # If we need to implement more of these sorts of custom commands, consider
    # making a factory for the description and results.
    def _execute_get_server_session_id(self) -> None:
        if self.connection.serverSessionId is None:
            raise Error(reason=f"Connection {self.connection} for cursor {self} has no serverSessionId")
        self.description = [
            ("server_session_id", TypeCodes.CHAR.value, None, None, None, None, None)
        ]  # display_size  # internal_size  # precision  # scale  # null_ok
        Row = namedtuple("Row", ("server_session_id",))
        self.list_result = [Row._make((self.connection.serverSessionId,))]

    def _execute_get(self, params: Sequence[str]) -> None:
        if len(params) == 1 and params[0].upper() == "SCHEMA":
            self._execute_get_schema()
        elif (
            len(params) == 3
            and params[0].upper() == "SERVER"
            and params[1].upper() == "SESSION"
            and params[2].upper() == "ID"
        ):
            self._execute_get_server_session_id()
        else:
            raise ProgrammingError(reason="Syntax error")

    def _execute_clear(self, params: Sequence[str]) -> None:
        if len(params) != 1 or params[0].upper() != "CACHE":
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _ClearCacheFactory()
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_ERROR and rsp.vendor_code == SESSION_EXPIRED_CODE:
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            self._execute_clear(params)
            return

        self._check_response(rsp)

    def _execute_cancelkill(self, op: str, id: Sequence[str]) -> None:
        if len(id) != 1:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _OCIENT_REQUEST_FACTORIES[op]
        req = factory.request(id[0])

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if (
            rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
            and rsp.response.vendor_code == SESSION_EXPIRED_CODE
        ):
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            self._execute_cancelkill(op, id)
            return

        self._check_response(rsp.response)

    # TODO: replace the other metadata call
    def _execute_systemmetadata(
        self,
        op: proto.FetchSystemMetadata.SystemMetadataCall,
        schema: Optional[str] = None,
        table: Optional[str] = None,
        column: Optional[str] = None,
        view: Optional[str] = None,
    ) -> Union[int, str, None]:
        factory = _GetSystemMetadataFactory()
        req = factory.request(op, schema, table, column, view)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if (
            rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR
            and rsp.response.vendor_code == SESSION_EXPIRED_CODE
        ):
            # Need to refresh the session
            self.connection.refresh()
            # and try again
            return self._execute_systemmetadata(op, schema=schema, table=table, column=column, view=view)

        self._check_response(rsp.response)

        if rsp.HasField("result_set_val"):
            self._get_result_metadata()

            for blob in rsp.result_set_val.blobs:
                self._buffers.append(blob)
            return None

        if rsp.HasField("string_val"):
            return rsp.string_val  # type: ignore[no-any-return]

        return rsp.int_val  # type: ignore[no-any-return]

    def _get_more_data(self) -> None:
        """Internal routine to get more data from a query"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_DATA
        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchDataResponse())

        self._check_response(rsp.response)

        for blob in rsp.result_set.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def fetchmany(self, size: Optional[int] = None) -> List[NamedTuple]:
        """Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when no
        more rows are available.

        The number of rows to fetch per call is specified by the parameter. If it
        is not given, the cursor's arraysize determines the number of rows to be
        fetched. The method will try to fetch as many rows as indicated by the size
        parameter. If this is not possible due to the specified number of rows not
        being available, fewer rows may be returned.
        """
        if size is None:
            size = self.arraysize
        rows: List[NamedTuple] = []
        while size > 0:
            a_row = self.fetchone()
            if a_row is None:
                break
            rows.append(a_row)
            size -= 1
        return rows

    def fetchall(self) -> List[NamedTuple]:
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.
        """
        return self.fetchmany(size=sys.maxsize)

    def __next__(self) -> NamedTuple:
        a_row = self.fetchone()
        if a_row is None:
            raise StopIteration
        return a_row

    def __iter__(self) -> "Cursor":
        return self

    def fetchval(self) -> Optional[object]:
        """The fetchval() convenience method returns the first column of the
        first row if there are results, otherwise it returns None.
        """
        arow = self.fetchone()
        if arow:
            return cast(object, arow[0])
        return None

    def fetchone(self) -> Optional[NamedTuple]:
        """Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.
        """
        # If there was never a query executed, throw an error
        if self.description is None:
            raise ProgrammingError("No result set available")

        # pylint: disable = too-many-branches
        if self.end_of_data:
            return None

        # special case explain.
        if self.generated_result is not None:
            self.end_of_data = True
            self._rowcount = 1
            assert self.resultset_tuple is not None
            return self.resultset_tuple._make((self.generated_result,))

        if self.list_result is not None:
            if self._offset >= len(self.list_result):
                self.end_of_data = True
                return None
            a_row = self.list_result[self._offset]
            self._offset += 1
            return a_row

        if self._rowcount < 0:
            self._rowcount = 0

        while not self._buffers:
            self._get_more_data()
            while self._buffers and self._buf() == b"\0\0\0\0":
                self._buffers.pop(0)

            if not self._buffers:
                # no data yet...wait so we don't hammer the host before asking for more
                sleep(0.25)

        if self._offset == 0:
            self._get_num_rows()

        row_length = self._get_int() - 4  # row_length includes the 4 bytes we just consumed
        end_offset = self._offset + row_length

        if self._bytes_remaining() == 1 and self._buf()[self._offset] == TypeCodes.DEM:
            self._rowcount -= 1
            self._buffers.pop(0)
            self._close_resultset()
            return self._process_pending()

        tmp_row: List[object] = []
        while self._offset < end_offset:
            tmp_row.append(self._decode_entry())

        if self._offset >= len(self._buf()):
            self._buffers.pop(0)
            self._offset = 0
        assert self.rownumber is not None
        self.rownumber += 1
        assert self.resultset_tuple is not None
        return self.resultset_tuple._make(tmp_row)

    def _process_pending(self) -> Optional[NamedTuple]:
        # if we have any pending queries to execute, kick one off now
        if self._pending_ops:
            self._buffers = []
            self._offset = 0
            self._execute_internal(self._pending_ops.pop(0))
            return self.fetchone()

        self.end_of_data = True
        return None

    def _buf(self) -> bytes:
        return self._buffers[0]

    def _bytes_remaining(self) -> int:
        if not self._buffers:
            return 0
        return len(self._buffers[0]) - self._offset

    def _get_num_rows(self) -> None:
        if self._bytes_remaining() >= 4:
            self._rowcount += self._get_int()

    def _decode_entry(self) -> object:
        # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
        coltype = self._get_byte()

        # if this is the easy conversion, just do it
        if coltype in _type_map:
            tm = _type_map[coltype]
            return self._get_type(tm[0], tm[1])

        if coltype == TypeCodes.STRING:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset : offset + strlen].decode("utf-8", errors="replace")

        if coltype == TypeCodes.TIMESTAMP:
            return datetime_ns.fromtimestamp(self._get_long(), tz=datetime.timezone.utc)

        if coltype == TypeCodes.NULL:
            return None

        if coltype == TypeCodes.BYTE:
            return int.from_bytes(self._get_type(1, _unpack_char), "big", signed=True)

        if coltype == TypeCodes.TIME:
            long_seconds = self._get_long()
            second = long_seconds % 60
            minutes = long_seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)
            return datetime.time(hour, minute, second)

        if coltype == TypeCodes.BINARY:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset : offset + strlen]

        if coltype == TypeCodes.DECIMAL:
            precision = self._get_byte()
            scale = self._get_byte()

            if precision % 2 == 0:
                strlen = int((precision / 2) + 1)
            else:
                strlen = int((precision + 1) / 2)

            data = self._buf()[self._offset : (self._offset + strlen - 1)]
            digits = []
            for byte in data:
                digits.append((byte & 0xF0) >> 4)
                digits.append(byte & 0x0F)

            sign = self._buf()[self._offset + strlen - 1]

            digits.append(sign >> 4)
            sign = sign & 0x0F

            if sign == 12:
                sign = 0
            elif sign == 13:
                sign = 1
            else:
                raise Error(reason=f"Unknown decimal sign value {sign}")

            self._offset += strlen
            return decimal.Decimal((sign, digits, -scale))

        if coltype == TypeCodes.ARRAY:
            nested_level = 0

            arraytype = self._get_byte()

            while arraytype == TypeCodes.ARRAY:
                arraytype = self._get_byte()
                nested_level += 1

            return self._get_array(nested_level)

        if coltype == TypeCodes.UUID:
            self._offset += 16
            return uuid.UUID(bytes=self._buf()[self._offset - 16 : self._offset])

        if coltype == TypeCodes.ST_POINT:
            long = self._get_double()
            lat = self._get_double()
            return STPoint(long, lat)

        if coltype == TypeCodes.DATE:
            d = datetime.datetime.utcfromtimestamp(self._get_long() / 1000.0)
            return datetime.date(d.year, d.month, d.day)

        if coltype == TypeCodes.IP:
            off = self._offset
            self._offset += 16
            return ipaddress.ip_address(self._buf()[off : off + 16])

        if coltype == TypeCodes.IPV4:
            off = self._offset
            self._offset += 4
            return ipaddress.ip_address(self._buf()[off : off + 4])

        if coltype == TypeCodes.TIMESTAMP_NANOS:
            return datetime_ns.from_timestamp_ns(self._get_long())

        if coltype == TypeCodes.TIME_NANOS:
            nanos = self._get_long()
            micros = int((nanos / 1000) % 1000000)
            float_seconds = nanos / 1000000000
            second = int(float_seconds % 60)
            minutes = float_seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)

            return datetime.time(hour, minute, second, micros)

        if coltype == TypeCodes.TUPLE:
            return self._get_tuple()

        if coltype == TypeCodes.ST_LINESTRING:
            points = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_double()
                lat = self._get_double()
                points.append(STPoint(long, lat))
            return STLinestring(points)

        if coltype == TypeCodes.ST_POLYGON or coltype == TypeCodes.ST_POLYGON_FULLFLAG:
            fullFlag = False

            if coltype == TypeCodes.ST_POLYGON_FULLFLAG:
                fullFlag = self._get_byte() != 0

            exterior = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_double()
                lat = self._get_double()
                exterior.append(STPoint(long, lat))
            holes = []
            num_rings = self._get_int()
            for i in range(num_rings):
                num_elements = self._get_int()
                ring = []
                for j in range(num_elements):
                    long = self._get_double()
                    lat = self._get_double()
                    ring.append(STPoint(long, lat))
                holes.append(ring)
            return STPolygon(exterior, holes, fullFlag)

        self.end_of_data = True
        raise Error(reason=f"Unknown column type {coltype}")

    def _get_byte(self) -> int:
        offset = self._offset
        self._offset += 1
        return self._buf()[offset]

    def _get_int(self) -> int:
        offset = self._offset
        self._offset += 4
        r = _unpack_int(self._buf(), offset)[0]
        assert isinstance(r, int)
        return r

    def _get_long(self) -> int:
        offset = self._offset
        self._offset += 8
        r = _unpack_long(self._buf(), offset)[0]
        assert isinstance(r, int)
        return r

    def _get_double(self) -> float:
        offset = self._offset
        self._offset += 8
        r = _unpack_double(self._buf(), offset)[0]
        assert isinstance(r, float)
        return r

    def _get_type(self, datalen: int, unpacker: Callable[[bytes, int], Tuple[_T, ...]]) -> _T:
        offset = self._offset
        self._offset += datalen
        return unpacker(self._buf(), offset)[0]

    def _get_array(self, level: int) -> List[object]:
        array: List[object] = []

        num_elements = self._get_int()

        all_null = self._get_byte()

        if all_null != 0:
            return []

        for _ in range(num_elements):
            if level > 0:
                array.append(self._get_array(level - 1))
            else:
                array.append(self._decode_entry())

        return array

    def _close_resultset(self) -> None:
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CLOSE_RESULT_SET")

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        self._check_response(rsp)

    def _get_tuple(self) -> Tuple[object, ...]:
        num_elements = self._get_int()
        restuple: Tuple[object, ...] = ()
        for _ in range(num_elements):
            restuple += (self._decode_entry(),)
        return restuple


def custom_type_to_json(obj: object) -> Union[str, List[int]]:
    """Helper function to convert types returned from queries to
    JSON values.  Typically invoked passed as the `default` parameter
    to json.dumps as in:

    `json.dumps(some_rows, default=custom_type_to_json)`
    """
    if isinstance(obj, decimal.Decimal):
        return str(obj)

    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()

    if isinstance(obj, bytes):
        return list(obj)

    if isinstance(obj, (uuid.UUID, ipaddress.IPv4Address, ipaddress.IPv6Address)):
        return str(obj)

    if isinstance(obj, (STPoint, STLinestring, STPolygon)):
        # TODO GeoJSON??
        return str(obj)

    raise TypeError(f"Unknown type {obj.__class__.__name__}")


def connect(
    dsn: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    database: Optional[str] = None,
    tls: Optional[TLSArgType] = None,
    force: Optional[bool] = None,
    handshake: Optional[HandshakeArgType] = None,
    configfile: Optional[str] = None,
    security_token: Optional[SecurityToken] = None,
    sso_callback_url: Optional[str] = None,
    sso_code: Optional[str] = None,
    sso_state: Optional[str] = None,
    sso_redirect_state: Optional[Dict[Any, Any]] = None,
    sso_oauth_flow: str = "",
    sso_timeout: float = SSO_RESPONSE_TIMEOUT,
    timeout: Optional[float] = None,
) -> Connection:
    # pylint: disable=too-many-arguments
    """Connection parameters can be specified as part of the dsn,
    using keyword arguments or both.  If both are specified, the keyword
    parameter overrides the value in the dsn.

    The Ocient DSN is of the format:
    `ocient://user:password@[host][:port][/database][?param1=value1&...]`

    `user` and `password` may be supplied if SSO or a security token are not
    provided.  `host` defaults to localhost,
    port defaults to 4050, database defaults to `system` and `tls` defaults
    to `unverified`.

    Multiple hosts may be specified, separated by a comma, in which case the
    hosts will be tried in order  Thus an example DSN might be
    `ocient://someone:somepassword@host1,host2:4051/mydb`

    A security token may be used from a previous connection.  For example:

        con1 = connect(host="foo", user="bar", password="baz")
        sectoken = con1.security_token
        con1.close()
        ...
        con2 = connect(host="foo", security_token=con1.sectoken)

    configfile is the name of a configuration file in INI format, where each
    section is either default, or a pattern that matches the host and optionally
    database. sections are matched in order, so more specific sections should
    precede less specific sections::

        [DEFAULT]
        tls = unverified

        # This will match the specific host and database
        [foo.ocient.com/somedb]
        user = panther
        password = pink

        # This will match the specific host
        [foo.ocient.com]
        user = panther
        password = pink

        # This will match any host in the ocient.com domain
        [*.ocient.com]
        user = tom
        password = jerry
        database = mice

        # This will match any host in the ocient.com domain
        [*.ocient.com]
        user = tom
        password = jerry

    Currently supported parameters are:

    - tls: Which can have the values "off", "unverified", or "on" in the dsn,
        or Connection.TLS_NONE, Connection.TLS_UNVERIFIED, or
        Connection.TLS_ON as a keyword parameter.
    - force: True or False, whether to force the connection to remain on this
        server
    - loglevel: the logging level for this module
    - logfile: a filename to which this module's log output will be written
    - timeout: An optional timeout, in seconds, for commands sent to the database.
       Note that long-running DDL commands may exceed this time and cause a timeout.

    SSO Parameters:

    When `handshake="sso"` is specified, the module will contact the Ocient database
    to retrieve SSO authentication information, and the following parameters will be
    used.

    - sso_callback_url: For an authorization SSO flow, the URI that the SSO authentication
        provider should redirect to after the flow is complete.  If this is not provided and
        the authorization flow is used, a web server listening on port 7050 will be started
        for the duration of the flow.
    - sso_redirect_state: The state field from a preceding SSORedirection exception
    - sso_code: the value returned to the `sso_callback_url` in the `code` URL parameter
    - sso_state: the value returend to the `sso_callback_url` in the `state` URL parameter
    - sso_oauth_flow: By default the module will try to open a browser window with the
        authorization URL, and if that fails, fall back on the "device" flow, which involves
        displaying a verification URL on stdout and waiting for the user to visit that URL.
        `sso_oauth_flow` can be set to "deviceGrant" to force the device flow even if it is
        possible for the module to open a browser
    - sso_timeout: the maxium time to wait during the device flow

    In the case of the authorization flow, we will raise an SSORedirection exception containing
    the authorization URL and expect the connect to be re-issued with the result
    """
    if isinstance(handshake, str):
        if handshake.lower() == "gcm":
            handshake = Connection.HANDSHAKE_GCM
        elif handshake.lower() == "sso":
            handshake = Connection.HANDSHAKE_SSO
        else:
            raise RuntimeError(f"Unknown Handshake method {handshake}")

    if isinstance(tls, str):
        if tls.lower() == "on":
            tls = Connection.TLS_ON
        elif tls.lower() == "unverified":
            tls = Connection.TLS_UNVERIFIED
        elif tls.lower() == "off":
            tls = Connection.TLS_NONE
        else:
            raise RuntimeError(f"Unknown TLS mode {tls}")

    params = {"user": user, "password": "*****", "host": host, "database": database, "tls": tls, "handshake": handshake}

    logger.debug("Connect %s", params)

    # If our Connection object construction requires an SSO callback, it will throw an SSORedirection exception
    try:
        return Connection(
            dsn,
            user,
            password,
            host,
            database,
            tls,
            handshake,
            force,
            configfile,
            security_token,
            sso_code=sso_code,
            sso_state=sso_state,
            sso_redirect_state=sso_redirect_state,
            sso_callback_url=sso_callback_url,
            sso_oauth_flow=sso_oauth_flow,
            sso_timeout=sso_timeout,
            timeout=timeout,
        )
    except SSORedirection as sso_redirect:
        # if we have been given an external redirection URL, re-raise the exception so
        # our caller can handle it
        if sso_callback_url:
            raise

        sso_code, sso_state = sso.local_sso_callback(sso_redirect.authURL, sso_timeout)

        if sso_code and sso_state:
            # This is our last ditch handler...we listen for the browser to reconnect to us.
            return Connection(
                dsn,
                user,
                password,
                host,
                database,
                tls,
                handshake,
                force,
                configfile,
                security_token,
                sso_code=sso_code,
                sso_state=sso_state,
                sso_redirect_state=sso_redirect.state,
                sso_oauth_flow=sso_oauth_flow,
                sso_timeout=sso_timeout,
            )

    logging.log(logging.DEBUG, "Unable to create connection")
    raise Error("Unable to create connection")


class ResultSetBuilder:
    def __init__(self, database_name: str) -> None:
        self.cols2Types: Dict[str, str] = {}
        self.cols2Pos: Dict[str, int] = {}
        self.pos2Cols: Dict[int, str] = {}
        self.resultSet: List[List[object]] = []
        self.databaseName = database_name

    def set_result_set_metadata(self, cols: List[str], types: List[str]) -> None:
        if len(cols) != len(types):
            raise Exception("In the result set builder, the columns list and the types list must have the same size")

        cols2Types: Dict[str, str] = {}
        cols2Pos: Dict[str, int] = {}
        for i, col in enumerate(cols):
            cols2Types[col] = types[i]
            cols2Pos[col] = i

        self.set_result_set_metadata_internal(cols2Types, cols2Pos)

    def set_result_set_metadata_internal(self, cols2Types: Dict[str, str], cols2Pos: Dict[str, int]) -> None:
        if len(cols2Types) == 0:
            raise Exception("In the result set builder, the metadata cannot be empty")

        if len(cols2Types) != len(cols2Pos):
            raise Exception("In the result set builder, the result set type and position maps must have the same size")

        for col in cols2Types:
            if col not in cols2Pos:
                raise Exception("In the result set builder, the column {} has a data type but no position".format(col))

        upper_case_cols2Types: Dict[str, str] = {key: value.upper() for key, value in cols2Types.items()}

        self.cols2Types = upper_case_cols2Types
        self.cols2Pos = cols2Pos

        self.pos2Cols = {v: k for k, v in cols2Pos.items()}

        # Check that positions start at zero and are contiguous
        for i in range(len(self.cols2Types)):
            if i not in self.pos2Cols:
                raise Exception(
                    "In the result set builder, positions are either not contiguous or do not start at zero"
                )

    def get_cols_in_order(self) -> List[str]:
        return [col for col in self.pos2Cols.values()]

    def get_types_in_order(self) -> List[str]:
        return [self.cols2Types[col] for col in self.pos2Cols.values()]

    def add_row(self, row: List[object]) -> None:
        if len(row) != len(self.cols2Pos):
            raise Exception("In the result set builder, an added row was the wrong size")

        # TODO - we should verify that each column is the correct type
        # or at least castable to the correct type, in which cast we need to cast it
        # if the sql type is any integer type then the type should be int
        # the rolehost side will convert the int type to BIGINT when its a python stored proc
        # same with sql type float/double - it's all the just the python float type

        self.resultSet.append(row)

    def from_existing_result_set(self, rs: Cursor) -> None:
        self.set_result_set_metadata_internal(rs.cols2Types, rs.cols2Pos)

        for row in rs.fetchall():
            temp = []
            for col in row:
                temp.append(col)
            self.add_row(temp)

    def append_existing_result_set(self, rs: Cursor) -> None:
        for row in rs.fetchall():
            temp = []
            for col in row:
                temp.append(col)
            self.add_row(temp)

    def num_rows(self) -> int:
        return len(self.resultSet)

    def get_row(self, index: int) -> List[object]:
        return self.resultSet[index]


def do_local_attach(port: int, database: str, token: str) -> Connection:
    return connect(dsn=f"ocient://:{token}@localhost:{port}/{database}?force=true")
