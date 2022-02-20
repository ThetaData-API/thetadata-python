from enum import Enum


class ReqArg(Enum):
    ID = 0, 1
    MSG_CODE = 1, 1
    REQ = 2, 1
    RTH = 3, 3
    USE_EXACT_TIME = 4, 3
    SEC_TYPE = 5, 4
    ROOT = 6, 4
    EXPIRATION = 7, 1
    RATE = 8, 4
    STRIKE = 9, 0
    RIGHT = 10, 4
    DURATION = 11, 1
    INTERVAL_SIZE = 12, 1
    START_DATE = 13, 1
    END_DATE = 14, 1

    def __init__(self, code: int, of: int):
        self.code = code
        self.of = of

    def __str__(self):
        return self._name_

