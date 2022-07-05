"""Contains core datatypes."""
from __future__ import annotations
from typing import Any
from datetime import datetime, timedelta
from pydantic.dataclasses import dataclass
import enum


class EnumParseError(Exception):
    """Raise when a value cannot be parsed into an associated enum member."""

    def __init__(self, value: Any, enm: enum.Enum):
        msg = f"Value {value} cannot be parsed into a {enm.__name__}!"
        super().__init__(msg)


class HeaderParseError(Exception):
    """Raise when header data is formatted incorrectly."""


@enum.unique
class MessageType(enum.Enum):
    """Codes used to ID types of requests/responses."""

    # Internal client communication
    CREDENTIALS = 0
    SESSION_TOKEN = 1
    INFO = 2
    METADATA = 3
    CONNECTED = 4

    # API communication
    PING = 100
    ERROR = 101
    DISCONNECTED = 102
    RECONNECTED = 103
    REQ_SYMS = 104
    SET_SYMS = 105
    CANT_CHANGE_SYMS = 106
    CHANGED_SYMS = 107

    # Client data
    HIST = 200
    ALL_EXPIRATIONS = 201
    ALL_STRIKES = 202
    HIST_END = 203
    LAST_QUOTE = 204
    ALL_ROOTS = 205
    LIST_END = 206

    # Experimental
    REQUEST_SERVER_LIST = 300
    REQUEST_OPTIMAL_SERVER = 301
    OPTIMAL_SERVER = 302
    PACKET = 303
    BAN_IP = 304
    POPULATION = 305

    @classmethod
    def from_code(cls: MessageType, code: int) -> MessageType:
        """Create a MessageType by its associated code.

        :raises EnumParseError: If the code does not match a MessageType
        """
        for member in cls:
            if code == member.value:
                return member
        raise EnumParseError(code, cls)


@enum.unique
class SecType(enum.Enum):
    """Security types."""

    OPTION = "OPTION"
    STOCK = "STOCK"
    FUTURE = "FUTURE"
    FORWARD = "FORWARD"
    SWAP = "SWAP"
    DEBT = "DEBT"
    CRYPTO = "CRYPTO"
    WARRANT = "WARRANT"


@enum.unique
class OptionRight(enum.Enum):
    """Option rights."""

    PUT = "P"
    CALL = "C"


@enum.unique
class OptionReqType(enum.Enum):
    """Option request types."""

    # VALUE
    DEFAULT = 100
    QUOTE = 101
    VOLUME = 102
    OPEN_INTEREST = 103

    # STANDARD
    LIQUIDITY = 201
    LIQUIDITY_PLUS = 202
    IMPLIED_VOLATILITY = 203
    GREEKS = 204
    OHLC = 205

    # PRO
    TRADE = 301
    TRADE_GREEKS = 302
    GREEKS_SECOND_ORDER = 303
    GREEKS_THIRD_ORDER = 304
    ALT_CALCS = 305


@dataclass
class DateRange:
    """Represents an inclusive date range."""

    start: datetime
    end: datetime

    def __init__(self, start: datetime, end: datetime):
        # remove times from datetimes
        self.start = start.date()
        self.end = end.date()
        assert (
            start <= end
        ), f"Start date {self.start} cannot be greater than end date {self.end}!"

    @classmethod
    def from_days(cls, n: int) -> DateRange:
        """Create a date range that spans the past n days."""
        assert type(n) == int
        assert n >= 0, "n must be nonnegative"
        end = datetime.now().date()
        start = end - timedelta(days=n)
        return cls(start, end)


@dataclass
class Header:
    """Represents the header returned on every Terminal call."""

    message_type: MessageType
    id: int
    latency: int
    error: int
    format_len: int
    size: int

    @classmethod
    def parse(cls, data: bytes) -> Header:
        """Parse binary header data into an object.

        :param data: raw header data, 20 bytes long
        :raise HeaderParseError: if data is incorrectly formatted
        """
        assert (
            len(bytes) == 20
        ), f"Cannot parse header with {len(bytes)} bytes. Expected 20 bytes."
        # avoid copying header data when slicing
        data = memoryview(data)
        """
        Header format:
            bytes | field
                2 | message type
                8 | id
                2 | latency
                2 | error
                1 | reserved / special
                1 | format length
                4 | size
        """
        # parse
        msgtype = MessageType.from_code(data[:2])
        id = data[2:10]
        latency = data[10:12]
        error = data[12:14]
        format_len = data[15]
        size = data[16:20]
        return cls(
            message_type=msgtype,
            id=id,
            latency=latency,
            error=error,
            format_len=format_len,
            size=size,
        )
