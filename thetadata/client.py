"""Module that contains Theta Client class."""
import re
import shutil
import subprocess
from decimal import Decimal
from threading import Thread
from time import sleep
from typing import Optional
from contextlib import contextmanager

import socket

from pandas import DataFrame
from tqdm import tqdm
import pandas as pd

from .enums import *
from .parsing import (
    Header,
    TickBody,
    ListBody,
)
from .terminal import check_download, launch_terminal

_NOT_CONNECTED_MSG = "You must establish a connection first."


def _format_strike(strike: float) -> int:
    """Round USD to the nearest tenth of a cent, acceptable by the terminal."""
    return round(strike * 1000)


def _format_date(dt: date) -> str:
    """Format a date obj into a string acceptable by the terminal."""
    return dt.strftime("%Y%m%d")


def _verify_java():
    if not shutil.which("java"):
        print('Java 11 or higher is required to use this API. Please install Java on this machine.')
        exit(1)
    version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
    pattern = '\"(\d+\.\d+).*\"'
    version = float(re.search(pattern, version.decode('utf8')).groups()[0])

    if version < 11:
        print('Java 11 or higher is required to use this API. You are using using Java '
              + str(version) + '. Please upgrade to a newer version.')
        exit(1)


# noinspection GrazieInspection
class ThetaClient:
    """A high-level, blocking client used to fetch market data."""

    def __init__(self, port: int = 11000, timeout: Optional[float] = 60, launch: bool = True, jvm_mem: int = 0,
                 username: str = "default", passwd: str = "default", auto_update: bool = True, use_bundle: bool = False):
        """Construct a client instance to interface with market data.

        :param port: The port number specified in the Theta Terminal config
        :param timeout: The max number of seconds to wait for a response before
            throwing a TimeoutError
        :param launch: Launches the terminal if true; uses an existing external terminal instance if false.
        :jvm_mem: Any integer provided above zero will force the terminal to allocate a maximum amount of memory in GB.
        :param username: Theta Data username / email. When specified with a
            password, this class will launch the terminal in headless mode.
        :param passwd: Theta Data password. When specified with a username,
            this class will launch the terminal in headless mode.
        :param auto_update: If true, this class will automatically download the
            latest terminal version each time this class is instantiated. If
            false, the terminal will use the current jar terminal file. If none
            exists, it will download the latest version.
        """
        self.port: int = port
        self.timeout = timeout
        self._server: Optional[socket.socket] = None  # None while disconnected
        self.launch = launch

        _verify_java()

        if launch:
            if username == "default" or passwd == "default":
                print("You are using the free version of Theta Data. You are currently limited to "
                      "20 requests / minute. A data subscription can be purchased at https://thetadata.net. "
                      "If you already have a Theta Data account, specify the username and passwd parameters.")

            check_download(auto_update)
            Thread(target=launch_terminal, args=[username, passwd, use_bundle, jvm_mem]).start()
        else:
            print("You are not launching the terminal. This means you should have an external instance already running.")

    @contextmanager
    def connect(self):
        """Initiate a connection with the Theta Terminal on `localhost`.

        :raises ConnectionRefusedError: If the connection failed.
        :raises TimeoutError: If the timeout is set and has been reached.
        """

        try:
            for i in range(15):
                try:
                    self._server = socket.socket()
                    self._server.connect(("localhost", self.port))
                    self._server.settimeout(1)
                    break
                except ConnectionError:
                    if i == 14:
                        raise ConnectionError('Unable to connect to the local Theta Terminal process.'
                                              ' Try restarting your system.')
                    sleep(1)
            self._server.settimeout(self.timeout)
            self._send_ver()
            yield
        finally:
            if self.launch:
                self.kill()
            self._server.close()

    def _send_ver(self):
        ver_msg = f"MSG_CODE={MessageType.HIST.value}&version=0.6.4\n"
        self._server.sendall(ver_msg.encode("utf-8"))

    def _recv(self, n_bytes: int, progress_bar: bool = False) -> bytearray:
        """Wait for a response from the Terminal.
        :param n_bytes:       The number of bytes to receive.
        :param progress_bar:  Print a progress bar displaying download progress.
        :return:              A response from the Terminal.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG

        # receive body data in parts
        MAX_PART_SIZE = 256  # 4 KiB recommended for most machines

        buffer = bytearray(n_bytes)
        bytes_downloaded = 0

        # tqdm disable=True is slow bc it still calls __new__, which takes nearly 4ms
        range_ = range(0, n_bytes, MAX_PART_SIZE)
        iterable = tqdm(range_, desc="Downloading") if progress_bar else range_

        start = 0
        for i in iterable:
            part_size = min(MAX_PART_SIZE, n_bytes - bytes_downloaded)
            bytes_downloaded += part_size
            part = self._server.recv(part_size)
            if part.__len__() < 0:
                continue
            start += 1
            buffer[i: i + part_size] = part

        assert bytes_downloaded == n_bytes
        return buffer

    def kill(self, ignore_err=True) -> None:
        """Remotely kill the Terminal process.

        All subsequent requests will timeout until the Terminal is restarted.
        """
        if not ignore_err:
            assert self._server is not None, _NOT_CONNECTED_MSG

        kill_msg = f"MSG_CODE={MessageType.KILL.value}\n"
        try:
            self._server.sendall(kill_msg.encode("utf-8"))
        except OSError:
            if ignore_err:
                pass
            else:
                raise OSError

    def get_hist_option(
        self,
        req: OptionReqType,
        root: str,
        exp: date,
        strike: float,
        right: OptionRight,
        date_range: DateRange,
        interval_size: int = 0,
        use_rth: bool = True,
        progress_bar: bool = False,
    ) -> pd.DataFrame:
        """
        Get historical option data.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an option.
        :param date_range:     The dates to fetch.
        :param interval_size:  The interval size in milliseconds. Applicable only to OHLC & QUOTE requests.
        :param use_rth:         If true, timestamps prior to 09:30 EST and after 16:00 EST will be ignored.
        :param progress_bar:   Print a progress bar displaying download progress.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        # format data
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)
        start_fmt = _format_date(date_range.start)
        end_fmt = _format_date(date_range.end)

        # send request
        hist_msg = f"MSG_CODE={MessageType.HIST.value}&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}&rth={use_rth}&IVL={interval_size}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header_data = self._server.recv(20)
        header: Header = Header.parse(hist_msg, header_data)

        # parse response body
        body_data = self._recv(header.size, progress_bar=progress_bar)
        body: DataFrame = TickBody.parse(hist_msg, header, body_data)
        return body

    def get_opt_at_time(
            self,
            req: OptionReqType,
            root: str,
            exp: date,
            strike: float,
            right: OptionRight,
            date_range: DateRange,
            ms_of_day: int = 0,
    ) -> pd.DataFrame:
        """
         Returns the last datatype of the request at a provided millisecond of the day.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an option.
        :param date_range:     The dates to fetch.
        :param ms_of_day:      The time of day in milliseconds.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        # format data
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)
        start_fmt = _format_date(date_range.start)
        end_fmt = _format_date(date_range.end)

        # send request
        hist_msg = f"MSG_CODE={MessageType.AT_TIME.value}&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}&IVL={ms_of_day}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header_data = self._server.recv(20)
        header: Header = Header.parse(hist_msg, header_data)

        # parse response body
        body_data = self._recv(header.size, progress_bar=False)
        body: DataFrame = TickBody.parse(hist_msg, header, body_data)
        return body

    def get_stk_at_time(
            self,
            req: StockReqType,
            root: str,
            date_range: DateRange,
            ms_of_day: int = 0,
    ) -> pd.DataFrame:
        """
         Returns the last datatype of the request at a provided millisecond of the day.

        :param req:            The request type.
        :param root:           The root symbol.
        :param date_range:     The dates to fetch.
        :param ms_of_day:      The time of day in milliseconds.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        # format data
        start_fmt = _format_date(date_range.start)
        end_fmt = _format_date(date_range.end)

        # send request
        hist_msg = f"MSG_CODE={MessageType.AT_TIME.value}&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&sec={SecType.STOCK.value}&req={req.value}&IVL={ms_of_day}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header_data = self._server.recv(20)
        header: Header = Header.parse(hist_msg, header_data)

        # parse response body
        body_data = self._recv(header.size, progress_bar=False)
        body: DataFrame = TickBody.parse(hist_msg, header, body_data)
        return body

    def get_hist_stock(
            self,
            req: StockReqType,
            root: str,
            date_range: DateRange,
            interval_size: int = 0,
            use_rth: bool = True,
            progress_bar: bool = False,
    ) -> pd.DataFrame:
        """
        Get historical stock data.

        :param req:            The request type.
        :param root:           The root symbol.
        :param date_range:     The dates to fetch.
        :param interval_size:  The interval size in milliseconds. Applicable only to OHLC & QUOTE requests.
        :param use_rth:         If true, timestamps prior to 09:30 EST and after 16:00 EST will be ignored.
        :param progress_bar:   Print a progress bar displaying download progress.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        # format data
        start_fmt = _format_date(date_range.start)
        end_fmt = _format_date(date_range.end)

        # send request
        hist_msg = f"MSG_CODE={MessageType.HIST.value}&START_DATE={start_fmt}&END_DATE={end_fmt}&root={root}&sec={SecType.STOCK.value}&req={req.value}&rth={use_rth}&IVL={interval_size}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response header
        header_data = self._server.recv(20)
        header: Header = Header.parse(hist_msg, header_data)

        # parse response body
        body_data = self._recv(header.size, progress_bar=progress_bar)
        body: DataFrame = TickBody.parse(hist_msg, header, body_data)
        return body

    # LISTING DATA

    def get_dates_stk(self, root: str, req: StockReqType) -> pd.Series:
        """
        Get all dates of data available for a given stock contract and request type.

        :param req:            The request type.
        :param root:           The root symbol.
        :return:               All dates that Theta Data provides data for given a request.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        out = f"MSG_CODE={MessageType.ALL_DATES.value}&root={root}&sec={SecType.STOCK.value}&req={req.value}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size), dates=True)
        return body.lst

    def get_dates_opt(
            self,
            req: OptionReqType,
            root: str,
            exp: date,
            strike: float,
            right: OptionRight) -> pd.Series:
        """
        Get all dates of data available for a given option contract and request type.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD.
        :param right:          The right of an option.
        :param root:           The root symbol.
        :return:               All dates that Theta Data provides data for given a request.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)
        out = f"MSG_CODE={MessageType.ALL_DATES.value}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size), dates=True)
        return body.lst

    def get_dates_opt_bulk(
            self,
            req: OptionReqType,
            root: str,
            exp: date) -> pd.Series:
        """
        Get all dates of data available for a given option expiration and request type.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param root:           The root symbol.
        :return:               All dates that Theta Data provides data for given option chain (expiration).
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        exp_fmt = _format_date(exp)
        out = f"MSG_CODE={MessageType.ALL_DATES_BULK.value}&root={root}&exp={exp_fmt}&sec={SecType.OPTION.value}&req={req.value}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size), dates=True)
        return body.lst

    def get_expirations(self, root: str) -> pd.Series:
        """
        Get all option expirations.

        :param root: The root symbol.
        :return: All expirations that Theta Data provides data for (YYYYMMDD).
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        out = f"MSG_CODE={MessageType.ALL_EXPIRATIONS.value}&root={root}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size), dates=True)
        return body.lst

    def get_strikes(self, root: str, exp: date) -> pd.Series:
        """
        Get all option strike prices in US tenths of a cent.

        :param root: The root symbol.
        :param exp: The expiration date.
        :return: The strike prices on the expiration.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        assert isinstance(exp, date)
        exp_fmt = _format_date(exp)
        out = f"MSG_CODE={MessageType.ALL_STRIKES.value}&root={root}&exp={exp_fmt}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size)).lst
        div = Decimal(1000)

        s = pd.Series([], dtype='float64')
        c = 0
        for i in body:
            s[c] = Decimal(i) / div
            c += 1

        return s

    def get_roots(self, sec: SecType) -> pd.Series:
        """
        Get all roots for a certain security type.

        :param sec: The type of security.
        :return: All root symbols for the security type.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        out = f"MSG_CODE={MessageType.ALL_ROOTS.value}&sec={sec.value}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size))
        return body.lst

    # LIVE DATA

    def get_last_option(
        self,
        req: OptionReqType,
        root: str,
        exp: date,
        strike: float,
        right: OptionRight,
    ) -> pd.DataFrame:
        """
        Get the most recent option tick.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an option.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        # format data
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)

        # send request
        hist_msg = f"MSG_CODE={MessageType.LAST.value}&root={root}&exp={exp_fmt}&strike={strike}&right={right.value}&sec={SecType.OPTION.value}&req={req.value}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response
        header: Header = Header.parse(hist_msg, self._server.recv(20))
        body: DataFrame = TickBody.parse(
            hist_msg, header, self._recv(header.size)
        )
        return body

    def get_last_stock(
        self,
        req: StockReqType,
        root: str,
    ) -> pd.DataFrame:
        """
        Get the most recent stock tick.

        :param req:            The request type.
        :param root:           The root symbol.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG

        # send request
        hist_msg = f"MSG_CODE={MessageType.LAST.value}&root={root}&sec={SecType.STOCK.value}&req={req.value}\n"
        self._server.sendall(hist_msg.encode("utf-8"))

        # parse response
        header: Header = Header.parse(hist_msg, self._server.recv(20))
        body: DataFrame = TickBody.parse(
            hist_msg, header, self._recv(header.size)
        )
        return body

    def get_req(
        self,
        req: str,
    ) -> pd.DataFrame:
        assert self._server is not None, _NOT_CONNECTED_MSG
        # send request
        req = req + "\n"
        self._server.sendall(req.encode("utf-8"))

        # parse response header
        header_data = self._server.recv(20)
        header: Header = Header.parse(req, header_data)

        # parse response body
        body_data = self._recv(header.size, progress_bar=False)
        body: DataFrame = TickBody.parse(req, header, body_data)
        return body

