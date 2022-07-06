"""Contains the Theta Client class and response models."""
from typing import Optional, Callable
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, date
import socket
from tqdm import tqdm
import pandas as pd
from pandas.core.frame import DataFrame

from .models import (
    OptionReqType,
    OptionRight,
    DateRange,
    Header,
    Body,
    MessageType,
    SecType,
)

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
            self.server = socket.socket()
            self.server.connect(("localhost", self.port))
            self.server.settimeout(self.timeout)
            yield
        finally:
            self.server.close()

    def get_hist_option(
        self,
        req: OptionReqType,
        root: str,
        exp: date,
        strike: int,
        right: OptionRight,
        interval: int,
        date_range: DateRange,
        progress_bar: bool = False,
    ) -> DataFrame:
        """
        Send a historical option data request.

        :param req:           The request type.
        :param root:          The root symbol.
        :param exp:           The expiration date. Associated time is ignored.
        :param strike:        The strike price in United States cents.
        :param right:         The right of an option.
        :param interval:      Interval size in minutes.
        :param date_range:    The dates to fetch.
        :param: progress_bar: Print a progress bar displaying download progress.

        :return:              The requested data as a pandas DataFrame.
        """
        # format data
        assert self.server is not None, _NOT_CONNECTED_MSG
        exp_fmt = _format_dt(exp)
        start_fmt = _format_dt(date_range.start)
        end_fmt = _format_dt(date_range.end)

        # send request
        request_id = 0
        # hist_msg = f"ID={request_id}&MSG_CODE={MessageType.HIST.value}&id=0&dur=100&root={root}&exp={_format_dt(exp)}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        hist_msg = f"ID={request_id}&MSG_CODE={MessageType.HIST.value}&id=0&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        self.server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header: Header = Header.parse(self.server.recv(20))

        # receive body data in parts
        BUFF_SIZE = 4096  # 4 KiB recommended for most machines
        body_data = b""
        for _ in tqdm(
            range(0, header.size, BUFF_SIZE),
            desc="Downloading",
            disable=not progress_bar,
        ):
            part = self.server.recv(BUFF_SIZE)
            body_data += part

        # parse response body
        body: Body = Body.parse(header, body_data, progress_bar=progress_bar)

        return body.ticks
