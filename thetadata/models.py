"""Contains core datatypes."""
from __future__ import annotations
from datetime import datetime, timedelta, date
from tqdm import tqdm

# from pydantic.dataclasses import dataclass
from dataclasses import dataclass
import enum
import pandas as pd
from pandas import DataFrame, Series
from .exceptions import EnumParseError, ResponseError


@enum.unique
class DataType(enum.Enum):
    """Codes used in the format tick to ID the type of data in the body ticks."""

    DATE = (0, False)
    MS_OF_DAY = (1, False)
    CORRECTION = (2, False)
    PRICE_TYPE = (4, False)

    # QUOTES
    BID_SIZE = (101, False)
    BID_EXCHANGE = (102, False)
    BID = (103, True)
    BID_CONDITION = (104, False)
    ASK_SIZE = (105, False)
    ASK_EXCHANGE = (106, False)
    ASK = (107, True)
    ASK_CONDITION = (108, False)

    # PRICING
    MIDPOINT = (111, True)
    VWAP = (112, True)
    QWAP = (113, True)
    WAP = (114, True)

    # OPEN INTEREST
    OPEN_INTEREST = (121, True)

    # TRADES
    SEQUENCE = (131, False)
    SIZE = (132, False)
    CONDITION = (133, False)
    PRICE = (134, True)

    # VOLUME
    VOLUME = (141, False)
    COUNT = (142, False)

    # FIRST ORDER GREEKS
    THETA = (151, True)
    VEGA = (152, True)
    DELTA = (153, True)
    RHO = (154, True)
    EPSILON = (155, True)
    LAMBDA = (156, True)

    # SECOND ORDER GREEKS
    GAMMA = (161, True)
    VANNA = (162, True)
    CHARM = (163, True)
    VOMMA = (164, True)
    VETA = (165, True)
    VERA = (166, True)
    SOPDK = (167, True)

    # THIRD ORDER GREEKS
    SPEED = (171, True)
    ZOMMA = (172, True)
    COLOR = (173, True)
    ULTIMA = (174, True)

    # OTHER CALCS
    D1 = (181, True)
    D2 = (182, True)
    DUAL_DELTA = (183, True)
    DUAL_GAMMA = (184, True)

    # OHLC
    OPEN = (191, False)
    HIGH = (192, False)
    LOW = (193, False)
    CLOSE = (194, False)

    # IMPLIED VOLATILITY
    IMPLIED_VOL = (201, False)

    # OTHER
    RATIO = (211, True)
    RATING = (212, True)

    # DIVIDEND
    EX_DATE = (221, False)
    RECORD_DATE = (222, False)
    PAYMENT_DATE = (223, False)
    ANN_DATE = (224, False)
    DIVIDEND_AMOUNT = (225, True)
    LESS_AMOUNT = (226, True)

    @classmethod
    def from_code(cls: DataType, code: int) -> DataType:
        """Create a DataType by its associated code.

        :raises EnumParseError: If the code does not match a DataType
        """
        for member in cls:
            if code == member.value[0]:
                return member
        raise EnumParseError(code, cls)

    def code(self) -> int:
        """:return: The datatype code associated w this type."""
        return self.value[0]

    def is_price(self) -> bool:
        """Check if this DataType indicates a price."""
        return self.value[1]


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
    LAST = 204
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
    """Option request type codes."""

    # FREE
    EOD = 1

    # VALUE
    QUOTE = 101
    VOLUME = 102
    OPEN_INTEREST = 103
    OHLC = 104

    # STANDARD
    TRADE = 201
    IMPLIED_VOLATILITY = 202
    GREEKS = 203
    LIQUIDITY = 204
    LIQUIDITY_PLUS = 205

    # PRO
    TRADE_GREEKS = 301
    GREEKS_SECOND_ORDER = 302
    GREEKS_THIRD_ORDER = 303
    ALT_CALCS = 304


@dataclass
class DateRange:
    """Represents an inclusive date range."""

    start: date
    end: date

    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end
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
        """
        assert (
            len(data) == 20
        ), f"Cannot parse header with {len(data)} bytes. Expected 20 bytes."
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
        parse_int = lambda d: int.from_bytes(d, "big")
        # parse
        msgtype = MessageType.from_code(parse_int(data[:2]))
        id = parse_int(data[2:10])
        latency = parse_int(data[10:12])
        error = parse_int(data[12:14])
        format_len = data[15]
        size = parse_int(data[16:20])
        return cls(
            message_type=msgtype,
            id=id,
            latency=latency,
            error=error,
            format_len=format_len,
            size=size,
        )


def _check_body_errors(header: Header, body_data: bytes):
    """Check for errors from the Terminal.

    :raises ResponseError: if the header indicates an error, containing a helpful error message."""
    if header.message_type == MessageType.ERROR:
        msg = body_data.decode("ascii")
        raise ResponseError(msg)


# map price types to price multipliers
_pt_to_price_mul = [
    0,
    0.000000001,
    0.00000001,
    0.0000001,
    0.000001,
    0.00001,
    0.0001,
    0.001,
    0.01,
    0.1,
    1,
    10.0,
    100.0,
    1000.0,
    10000.0,
    100000.0,
    1000000.0,
    10000000.0,
    100000000.0,
    1000000000.0,
]


class TickBody:
    """Represents the body returned on Terminal calls that deal with ticks."""

    def __init__(self, ticks: DataFrame):
        assert isinstance(
            ticks, DataFrame
        ), "Cannot initialize body bc ticks is not a DataFrame"
        self.ticks: DataFrame = ticks

    @classmethod
    def parse(
        cls, header: Header, data: bytes, progress_bar: bool = False
    ) -> TickBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        :param: progress_bar: Print a progress bar displaying progress.
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        _check_body_errors(header, data)

        # avoid copying body data when slicing
        data = memoryview(data)
        parse_int = lambda d: int.from_bytes(d, "big")

        # parse ticks
        n_ticks = int(header.size / (header.format_len * 4))
        bytes_per_tick = header.format_len

        # parse format tick
        format_tick_codes = []
        for b in range(bytes_per_tick):
            int_ = parse_int(data[b * 4 : b * 4 + 4])
            format_tick_codes.append(int_)
        format: list[DataType] = list(
            map(lambda code: DataType.from_code(code), format_tick_codes)
        )

        # initialize empty dataframe w/ format columns
        df = pd.DataFrame(columns=format)

        # get the index of the price type column if it exists
        if DataType.PRICE_TYPE in df.columns:
            price_type_idx = df.columns.get_loc(DataType.PRICE_TYPE)

        # parse the rest of the ticks
        ticks = []
        for tn in tqdm(
            range(1, n_ticks), desc="Processing", disable=not progress_bar
        ):
            tick_offset = tn * bytes_per_tick * 4
            tick = []
            for b in range(bytes_per_tick):
                # parse int
                int_offset = tick_offset + b * 4
                int_ = parse_int(data[int_offset : int_offset + 4])
                tick.append(int_)

            # map price columns to prices if the tick contains a price type
            if price_type_idx is not None:
                # get price multiplier from price type
                pt = tick[price_type_idx]
                price_multiplier = _pt_to_price_mul[pt]
                # multiply tick price fields by price multiplier
                for i in range(len(tick)):
                    if format[i].is_price():
                        tick[i] = tick[i] * price_multiplier
                # remove price type from tick
                del tick[price_type_idx]

            ticks.append(tick)

        # delete price type column if it exists
        if price_type_idx is not None:
            del df[DataType.PRICE_TYPE]

        # add ticks to dataframe in a single concat
        df = pd.concat(
            [pd.DataFrame(ticks, columns=df.columns), df],
            ignore_index=True,
        )

        return cls(ticks=df)


class ListBody:
    """Represents the body returned on every Terminal call that have one DataType."""

    def __init__(self, lst: Series):
        assert isinstance(
            lst, Series
        ), "Cannot initialize body bc lst is not a Series"
        self.lst: Series = lst

    @classmethod
    def parse(
        cls, header: Header, data: bytes, progress_bar: bool = False
    ) -> ListBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        :param: progress_bar: Print a progress bar displaying progress.
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        _check_body_errors(header, data)

        lst = data.decode("ascii").split(",")
        lst = pd.Series(lst, copy=False)

        return cls(lst=lst)
