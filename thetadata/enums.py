"""Module that contains various enums necessary to interface w the Terminal."""
from __future__ import annotations

import enum
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from . import exceptions


@enum.unique
class DataType(enum.Enum):
    """Codes used in the format tick to ID the data in the body ticks."""

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
    OPEN = (191, True)
    HIGH = (192, True)
    LOW = (193, True)
    CLOSE = (194, True)

    # IMPLIED VOLATILITY
    IMPLIED_VOL = (201, True)
    BID_IMPLIED_VOL = (202, True)
    ASK_IMPLIED_VOL = (203, True)
    UNDERLYING_PRICE = (204, True)

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
    def from_code(cls, code: int) -> DataType:
        """Create a DataType by its associated code.

        :raises EnumParseError: If the code does not match a DataType
        """
        for member in cls:
            if code == member.value[0]:
                return member
        raise exceptions._EnumParseError(code, cls)

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
    VERSION = 5

    # API communication
    PING = 100
    ERROR = 101
    DISCONNECTED = 102
    RECONNECTED = 103
    REQ_SYMS = 104
    SET_SYMS = 105
    CANT_CHANGE_SYMS = 106
    CHANGED_SYMS = 107
    KILL = 108

    # Client data
    HIST = 200
    ALL_EXPIRATIONS = 201
    ALL_STRIKES = 202
    HIST_END = 203
    LAST = 204
    ALL_ROOTS = 205
    LIST_END = 206
    ALL_DATES = 207
    AT_TIME = 208
    ALL_DATES_BULK = 209
    STREAM_REQ = 210
    STREAM_CALLBACK = 211

    # Experimental
    REQUEST_SERVER_LIST = 300
    REQUEST_OPTIMAL_SERVER = 301
    OPTIMAL_SERVER = 302
    PACKET = 303
    BAN_IP = 304
    POPULATION = 305

    @classmethod
    def from_code(cls, code: int) -> MessageType:
        """Create a MessageType by its associated code.

        :raises EnumParseError: If the code does not match a MessageType
        """
        for member in cls:
            if code == member.value:
                return member
        raise exceptions._EnumParseError(code, cls)


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
    OHLC_QUOTE = 105

    # STANDARD
    TRADE = 201
    IMPLIED_VOLATILITY = 202
    GREEKS = 203
    LIQUIDITY = 204
    LIQUIDITY_PLUS = 205
    IMPLIED_VOLATILITY_VERBOSE = 206
    # PRO
    TRADE_GREEKS = 301
    GREEKS_SECOND_ORDER = 302
    GREEKS_THIRD_ORDER = 303
    ALT_CALCS = 304


@enum.unique
class StockReqType(enum.Enum):
    """Stock request type codes."""

    # FREE
    EOD = 1

    # VALUE
    QUOTE = 101
    VOLUME = 102
    OHLC = 104

    # STANDARD
    TRADE = 201


@dataclass
class DateRange:
    """Represents an inclusive date range."""

    start: date
    end: date

    def __init__(self, start: date, end: date):
        """Create an inclusive date range between `start` and `end`."""
        assert isinstance(
            start, date
        ), f"Expected start to be a date object. Got {type(start)}."
        assert isinstance(
            start, date
        ), f"Expected end to be a date object. Got {type(end)}."
        self.start = start
        self.end = end
        assert (
            start <= end
        ), f"Start date {self.start} is greater than end date {self.end}!"

    @classmethod
    def from_days(cls, n: int) -> DateRange:
        """Create a date range that spans the past `n` days."""
        assert type(n) == int
        assert n >= 0, "n must be nonnegative"
        end = datetime.now().date()
        start = end - timedelta(days=n)
        return cls(start, end)


@enum.unique
class StreamMsgType(enum.Enum):
    """Codes used to ID types of requests/responses."""

    # Internal client communication
    CREDENTIALS = 0
    SESSION_TOKEN = 1
    INFO = 2
    METADATA = 3
    CONNECTED = 4

    # API communication
    PING = 10
    ERROR = 11
    DISCONNECTED = 12
    RECONNECTED = 13

    # Client data
    CONTRACT = 20
    QUOTE = 21
    TRADE = 22

    # Experimental
    REQUEST_SERVER_LIST = 300
    REQUEST_OPTIMAL_SERVER = 301
    OPTIMAL_SERVER = 302
    PACKET = 303
    BAN_IP = 304
    POPULATION = 305

    @classmethod
    def from_code(cls, code: int) -> MessageType:
        """Create a MessageType by its associated code.

        :raises EnumParseError: If the code does not match a MessageType
        """
        for member in cls:
            if code == member.value:
                return member
        raise exceptions._EnumParseError(code, cls)

@enum.unique
class Exchange(enum.Enum):
    """Codes used to ID types of requests/responses."""

    COMP = (0, "", "Comp")
    NQEX = (1, "XNMS", "Nasdaq Exchange")
    NQAD = (2, "XADF", "Nasdaq Alternative Display Facility")
    NYSE = (3, "XNYS", "New York Stock Exchange")
    AMEX = (4, "XASE", "American Stock Exchange")
    CBOE = (5, "XCBO", "Chicago Board Options Exchange")
    ISEX = (6, "XISX", "International Securities Exchange")
    PACF = (7, "ARCX", "NYSE ARCA (Pacific)")
    CINC = (8, "XCIS", "National Stock Exchange (Cincinnati)")
    PHIL = (9, "XPHL", "Philidelphia Stock Exchange")
    OPRA = (10, "OPRA", "Options Pricing Reporting Authority")
    BOST = (11, "XBOS", "Boston Stock/Options Exchange")
    NQNM = (12, "XNGS", "Nasdaq Global+Select Market (NMS)")
    NQSC = (13, "XNCM", "Nasdaq Capital Market (SmallCap)")
    NQBB = (14, "OOTC", "Nasdaq Bulletin Board")
    NQPK = (15, "OOTC", "Nasdaq OTC")
    NQAG = (16, "XADF", "Nasdaq Aggregate Quote")
    CHIC = (17, "CXHI", "Chicago Stock Exchange")
    TSE = (18, "XTSE", "Toronto Stock Exchange")
    CDNX = (19, "XTSX", "Canadian Venture Exchange")
    CME = (20, "XCME", "Chicago Mercantile Exchange")
    NYBT = (21, "IMAG", "New York Board of Trade")
    MRCY = (22, "MCRY", "ISE Mercury")
    COMX = (23, "XCEC", "COMEX (division of NYMEX)")
    CBOT = (24, "GLBX", "Chicago Board of Trade")
    NYMX = (25, "XNYM", "New York Mercantile Exchange")
    KCBT = (26, "XKBT", "Kansas City Board of Trade")
    MGEX = (27, "XMGE", "Minneapolis Grain Exchange")
    WCE = (28, "IFCA", "Winnipeg Commodity Exchange")
    ONEC = (29, "XOCH", "OneChicago Exchange")
    DOWJ = (30, "", "Dow Jones Indicies")
    GEMI = (31, "GMNI", "ISE Gemini")
    SIMX = (32, "XSES", "Singapore International Monetary Exchange")
    FTSE = (33, "XLON", "London Stock Exchange")
    EURX = (34, "XEUR", "Eurex")
    ENXT = (35, "XAMS", "EuroNext")
    DTN = (36, "", "Data Transmission Network")
    LMT = (37, "XLME", "London Metals Exchange Matched Trades")
    LME = (38, "XLME", "London Metals Exchange")
    IPEX = (39, "IEPA", "Intercontinental Exchange (IPE)")
    MX = (40, "XMOD", "Montreal Stock Exchange")
    WSE = (41, "XTSX", "Winnipeg Stock Exchange")
    C2 = (42, "C2OX", "CBOE C2 Option Exchange")
    MIAX = (43, "XMIO", "Miami Exchange")
    CLRP = (44, "XNYM", "NYMEX Clearport")
    BARK = (45, "BARX", "Barclays")
    TEN4 = (46, "", "TenFore")
    NQBX = (47, "XBOS", "NASDAQ Boston")
    HOTS = (48, "XEUR", "HotSpot Eurex US")
    EUUS = (49, "XEUR", "Eurex US")
    EUEU = (50, "XEUR", "Eurex EU")
    ENCM = (51, "XEUC", "Euronext Commodities")
    ENID = (52, "XEUE", "Euronext Index Derivatives")
    ENIR = (53, "XEUI", "Euronext Interest Rates")
    CFE = (54, "XCBF", "CBOE Futures Exchange")
    PBOT = (55, "XPBT", "Philadelphia Board of Trade")
    HWTB = (56, "XHAN", "Hannover WTB Exchange")
    NQNX = (57, "FINN", "FINRA/NASDAQ Trade Reporting Facility")
    BTRF = (58, "XADF", "BSE Trade Reporting Facility")
    NTRF = (59, "FINY", "NYSE Trade Reporting Facility")
    BATS = (60, "BATS", "BATS Trading")
    NYLF = (61, "XNLI", "NYSE LIFFE metals contracts")
    PINK = (62, "OTCM", "Pink Sheets")
    BATY = (63, "BATY", "BATS Trading")
    EDGE = (64, "EDGA", "Direct Edge")
    EDGX = (65, "EDGX", "Direct Edge")
    RUSL = (66, "", "Russell Indexes")
    CMEX = (67, "XIOM", "CME Indexes")
    IEX = (68, "IEXG", "Investors Exchange")
    TBA_69 = (69, "", "TBA Exchange 69")
    TBA_70 = (70, "", "TBA Exchange 70")
    TBA_71 = (71, "", "TBA Exchange 71")
    TBA_72 = (72, "", "TBA Exchange 72")
    TBA_73 = (73, "", "TBA Exchange 73")
    TBA_74 = (74, "", "TBA Exchange 74")
    TBA_75 = (75, "", "TBA Exchange 75")
    TBA_76 = (76, "", "TBA Exchange 76")
    TBA_77 = (77, "", "TBA Exchange 77")
    TBA_78 = (78, "", "TBA Exchange 78")
    TBA_79 = (79, "", "TBA Exchange 79")
    @classmethod
    def from_code(cls, code: int) -> MessageType:
        """Create a MessageType by its associated code.

        :raises EnumParseError: If the code does not match a MessageType
        """
        for member in cls:
            if code == member.value[0]:
                return member
        raise exceptions._EnumParseError(code, cls)



