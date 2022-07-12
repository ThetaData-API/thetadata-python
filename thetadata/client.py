"""Module that contains Theta Client class."""
from typing import Optional, Callable
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, date
import socket
from tqdm import tqdm
import pandas as pd

from .enums import *
from .parsing import (
    Header,
    TickBody,
    ListBody,
)

from .exceptions import ResponseError

_NOT_CONNECTED_MSG = "You must esetablish a connection first."


def _format_date(dt: date) -> str:
    """Format a date obj into a string acceptable by the terminal."""
    return dt.strftime("%Y%m%d")


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
        self._server: Optional[socket.socket] = None  # None while disconnected

    @contextmanager
    def connect(self):
        """Initiate a connection with the Theta Terminal on `localhost`.

        :raises ConnectionRefusedError: If the connection failed.
        :raises TimeoutError: If the timeout is set and has been reached.
        """
        try:
            self._server = socket.socket()
            self._server.connect(("localhost", self.port))
            self._server.settimeout(self.timeout)
            yield
        finally:
            self._server.close()

    def _recv(self, n_bytes: int, progress_bar: bool = False) -> bytes:
        """Wait for a response from the Terminal.
        :param n_bytes:       The number of bytes to receive.
        :param progress_bar:  Print a progress bar displaying download progress.
        :return:              A response from the Terminal.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG

        # receive body data in parts
        PART_SIZE = 4096  # 4 KiB recommended for most machines

        buffer = bytearray(n_bytes)
        bytes_downloaded = 0
        for i in tqdm(
            range(0, n_bytes, PART_SIZE),
            desc="Downloading",
            disable=not progress_bar,
        ):
            bytes_downloaded += PART_SIZE
            part = self._server.recv(PART_SIZE)
            buffer[i : i + PART_SIZE] = part

        return bytes(buffer)

    def get_hist_option(
        self,
        req: OptionReqType,
        root: str,
        exp: date,
        strike: int,
        right: OptionRight,
        date_range: DateRange,
        progress_bar: bool = False,
    ) -> pd.DataFrame:
        """
        Get historical option data.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in United States cents.
        :param right:          The right of an option.
        :param date_range:     The dates to fetch.
        :param progress_bar:   Print a progress bar displaying download progress.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        # format data
        assert self._server is not None, _NOT_CONNECTED_MSG
        exp_fmt = _format_date(exp)
        start_fmt = _format_date(date_range.start)
        end_fmt = _format_date(date_range.end)

        # send request
        request_id = 0
        hist_msg = f"ID={request_id}&MSG_CODE={MessageType.HIST.value}&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header: Header = Header.parse(self._server.recv(20))

        # parse response body
        body_data = self._recv(header.size, progress_bar=progress_bar)
        body: TickBody = TickBody.parse(
            header, body_data, progress_bar=progress_bar
        )

        return body.ticks

    # LISTING DATA

    def get_expirations(self, root: str) -> pd.Series:
        """
        Get all option expirations.

        :param root: The root symbol.
        :return: All expirations that Theta Data provides data for (YYYYMMDD).
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        req_id = 1
        out = f"MSG_CODE={MessageType.ALL_EXPIRATIONS.value}&ID={req_id}&root={root}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(self._server.recv(20))
        body = ListBody.parse(header, self._recv(header.size))
        return body.lst

    def get_strikes(self, root: str, exp: str) -> pd.Series:
        """
        Get all option strike prices in US cents.

        :param root: The root symbol.
        :param exp: The expiration date (YYYYMMDD).
        :return: The strike prices on the expiration.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        req_id = 1
        out = f"MSG_CODE={MessageType.ALL_STRIKES.value}&ID={req_id}&root={root}&exp={exp}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(self._server.recv(20))
        body = ListBody.parse(header, self._recv(header.size))
        return body.lst

    def get_roots(self, sec: SecType) -> pd.Series:
        """
        Get all roots for a certain security type.

        :param sec: The type of security.
        :return: All root symbols for the security type.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        req_id = 1
        out = f"MSG_CODE={MessageType.ALL_ROOTS.value}&ID={req_id}&sec={sec.value}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(self._server.recv(20))
        body = ListBody.parse(header, self._recv(header.size))
        return body.lst

    # LIVE DATA

    def get_last_option(
        self,
        req: OptionReqType,
        root: str,
        exp: date,
        strike: int,
        right: OptionRight,
    ) -> pd.DataFrame:
        """
        Get the most recent option data.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Associated time is ignored.
        :param strike:         The strike price in United States cents.
        :param right:          The right of an option.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        # format data
        assert self._server is not None, _NOT_CONNECTED_MSG
        exp_fmt = _format_date(exp)

        # send request
        request_id = 0
        hist_msg = f"ID={request_id}&MSG_CODE={MessageType.LAST.value}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response
        header: Header = Header.parse(self._server.recv(20))
        body: TickBody = TickBody.parse(header, self._recv(header.size))

        return body.ticks
