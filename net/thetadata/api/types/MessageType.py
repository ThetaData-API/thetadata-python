from enum import Enum


class MessageType(Enum):

    #
    # Internal client communication
    #
    CREDENTIALS =        0
    SESSION_TOKEN =      1
    INFO =               2
    METADATA =           3
    CONNECTED =          4

    #
    # API communication
    #
    PING = 100
    ERROR = 101
    DISCONNECTED = 102
    RECONNECTED = 103
    REQ_SYMS = 104
    SET_SYMS = 105
    CANT_CHANGE_SYMS = 106
    CHANGED_SYMS = 107

    #
    # Client Data
    #
    HIST = 200
    ALL_EXPIRATIONS = 201
    ALL_STRIKES = 202
    HIST_END = 203
    LAST_QUOTE = 204
    #
    # Experimental
    #
    REQUEST_SERVER_LIST = 300
    REQUEST_OPTIMAL_SERVER = 301
    OPTIMAL_SERVER = 302
    PACKET = 303
    BAN_IP = 304
    POPULATION = 305

    def __init__(self, code: int):
        self.code = code

    def name(self):
        return self._name_
