"""Contains the Theta Client class and response models."""
from typing import Optional, Callable
from contextlib import contextmanager
from functools import wraps
from datetime import datetime
import socket

from .models import OptionReqType, OptionRight, DateRange, Header, MessageType

_NOT_CONNECTED_MSG = "You must esetablish a connection first."


def _format_dt(dt: datetime) -> str:
    """Format a datetime obj into a string acceptable by the terminal."""
    return dt.strftime("%Y%m%d")


class HistOptionResponse:
    """The deserialized response from a historical option request."""


class ThetaClient:
    """A high-level, blocking client used to fetch market data."""

    def __init__(self, port: int = 11000, timeout: Optional[float] = 10):
        """Construct a client instance to interface with market data.

        :param port: The port number specified in the Theta Terminal config
        :param timeout: The max number of seconds to wait for a response before
            throwing a TimeoutError
        """
        self.port: int = port
        self.timeout = timeout
        self.server: Optional[socket.socket] = None  # None while disconnected

    @contextmanager
    def connect(self):
        """Initiate a connection with the Theta Terminal on localhost.

        :raises ConnectionRefusedError: If the connection failed.
        :raises TimeoutError: If the timeout is set and has been reached.
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect(("localhost", self.port))
            self.server.settimeout(self.timeout)
            yield
        finally:
            self.server.close()

    def get_hist_option(
        self,
        req: OptionReqType,
        root: str,
        exp: datetime,
        strike: int,
        right: OptionRight,
        interval: int,
        date_range: DateRange,
    ) -> Optional[HistOptionResponse]:
        """
        Send a historical option data request.

        :param req:         The request type.
        :param root:        The root symbol.
        :param exp:         The expiration date. Associated time is ignored.
        :param strike:      The strike price in United States cents.
        :param right:       The right of an option.
        :param interval:    Interval size in minutes.
        :param date_range:  The dates to fetch.
        :return: The requested data or None if the request timed out.
        :raises RequestException: If request could not be completed.
        """
        assert self.server is not None, _NOT_CONNECTED_MSG
        exp_fmt = _format_dt(exp)
        start_fmt = _format_dt(date_range.start)
        end_fmt = _format_dt(date_range.end)
        return HistOptionResponse()
