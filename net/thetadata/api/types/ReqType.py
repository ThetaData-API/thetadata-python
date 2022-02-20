from enum import Enum


class ReqType(Enum):
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

    def __init__(self, code: int):
        self.code = code

    def name(self):
        return self._name_

