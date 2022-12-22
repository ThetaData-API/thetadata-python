"""Module that contains Theta Client class."""
import struct
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
_VERSION = '0.7.3'


def _format_strike(strike: float) -> int:
    """Round USD to the nearest tenth of a cent, acceptable by the terminal."""
    return round(strike * 1000)


def _format_date(dt: date) -> str:
    """Format a date obj into a string acceptable by the terminal."""
    return dt.strftime("%Y%m%d")


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


class Trade:
    """Trade"""
    def __init__(self):
        """from_bytes
          """
        self.ms_of_day = 0
        self.sequence = 0
        self.size = 0
        self.condition = 0
        self.price = 0
        self.exchange = None
        self.date = None

    def from_bytes(self, data: bytearray):
        """from_bytes
          """
        view = memoryview(data)
        parse_int = lambda d: int.from_bytes(d, "big")
        self.ms_of_day = parse_int(view[0:4])
        self.sequence = parse_int(view[4:8]) & 0xffffffffffffffff
        self.size = parse_int(view[8:12])
        self.condition = parse_int(view[12:16])
        self.price = round(parse_int(view[16:20]) * _pt_to_price_mul[parse_int(view[24:28])], 4)
        self.exchange = Exchange.from_code(parse_int(view[20:24]))
        date_raw = str(parse_int(view[28:32]))
        self.date = date(year=int(date_raw[0:4]), month=int(date_raw[4:6]), day=int(date_raw[6:8]))


class Quote:
    """Quote"""
    def __init__(self):
        """from_bytes
          """
        self.ms_of_day = 0
        self.bid_size = 0
        self.bid_exchange = 0
        self.bid_price = 0
        self.bid_condition = 0
        self.ask_size = 0
        self.ask_exchange = 0
        self.ask_price = 0
        self.ask_condition = 0
        self.date = None

    def from_bytes(self, data: bytes):
        """from_bytes
          """
        view = memoryview(data)
        parse_int = lambda d: int.from_bytes(d, "big")
        mult = _pt_to_price_mul[parse_int(view[36:40])]
        self.ms_of_day     = parse_int(view[0:4])
        self.bid_size      = parse_int(view[4:8])
        self.bid_exchange  = parse_int(view[8:12])
        self.bid_price     = round(parse_int(view[12:16]) * mult, 4)
        self.bid_condition = parse_int(view[16:20])

        self.ask_size = parse_int(view[20:24])
        self.ask_exchange = parse_int(view[24:28])
        self.ask_price = round(parse_int(view[28:32]) * mult, 4)
        self.ask_condition = parse_int(view[32:36])
        date_raw = str(parse_int(view[40:44]))
        self.date = date(year=int(date_raw[0:4]), month=int(date_raw[4:6]), day=int(date_raw[6:8]))


class Contract:
    """Contract"""
    def __init__(self):
        """from_bytes
          """
        self.root = ""
        self.exp = None
        self.strike = None
        self.isCall = False
        self.isOption = False

    def from_bytes(self, data: bytes):
        """from_bytes
        """
        view = memoryview(data)
        parse_int = lambda d: int.from_bytes(d, "big")
        # parse
        len = parse_int(view[:1])
        root_len = parse_int(view[1:2])
        self.root = data[2:2 + root_len].decode("ascii")
        self.isOption = data[root_len + 2] == 1
        if not self.isOption:
            return
        date_raw = str(parse_int(view[root_len + 3: root_len + 7]))
        self.exp = date(year=int(date_raw[0:4]), month=int(date_raw[4:6]), day=int(date_raw[6:8]))
        self.isCall = parse_int(view[root_len + 7: root_len + 8]) == 1
        self.strike = parse_int(view[root_len + 9: root_len + 13]) / 1000.0

    def to_string(self) -> str:
        return 'root: ' + self.root + ' isOption: ' + str(self.isOption) + ' exp: ' + str(self.exp) + \
               ' strike: ' + str(self.strike) + ' isCall: ' + str(self.isCall)


class StreamMsg:
    """Msg"""
    def __init__(self):
        self.type = StreamMsgType.ERROR
        self.trade = Trade()
        self.quote = Quote()
        self.contract = Contract()


class ThetaClient:
    """A high-level, blocking client used to fetch market data. Instantiating this class
    runs a java background process, which is responsible for the heavy lifting of market
    data communication. Java 11 or higher is required to use this class."""

    def __init__(self, port: int = 11000, timeout: Optional[float] = 60, launch: bool = True, jvm_mem: int = 0,
                 username: str = "default", passwd: str = "default", auto_update: bool = True, use_bundle: bool = True):
        """Construct a client instance to interface with market data. If no username and passwd fields are provided,
            the terminal will connect to thetadata servers with free data permissions.

        :param port: The port number specified in the Theta Terminal config, which can usually be found under
                        %user.home%/ThetaData/ThetaTerminal.
        :param timeout: The max number of seconds to wait for a response before throwing a TimeoutError
        :param launch: Launches the terminal if true; uses an existing external terminal instance if false.
        :jvm_mem: Any integer provided above zero will force the terminal to allocate a maximum amount of memory in GB.
        :param username: Theta Data email. Can be omitted with passwd if using free data.
        :param passwd: Theta Data password. Can be omitted with username if using free data.
        :param auto_update: If true, this class will automatically download the latest terminal version each time
            this class is instantiated. If false, the terminal will use the current jar terminal file. If none exists,
            it will download the latest version.
        :param use_bundle: Will download / use open-jdk-19.0.1 if True and the operating system is windows.
        """
        self.port: int = port
        self.timeout = timeout
        self._server: Optional[socket.socket] = None  # None while disconnected
        self._stream_server: Optional[socket.socket] = None  # None while disconnected
        self.launch = launch

        if launch:
            if username == "default" or passwd == "default":
                print('------------------------------------------------------------------------------------------------')
                print("You are using the free version of Theta Data. You are currently limited to "
                      "20 requests / minute.\nA data subscription can be purchased at https://thetadata.net. "
                      "If you already have a ThetaData\nsubscription, specify the username and passwd parameters.")
                print('------------------------------------------------------------------------------------------------')
            check_download(auto_update)
            Thread(target=launch_terminal, args=[username, passwd, use_bundle, jvm_mem]).start()
        else:
            print("You are not launching the terminal. This means you should have an external instance already running.")

    @contextmanager
    def connect(self):
        """Initiate a connection with the Theta Terminal on `localhost`. Requests can only be made inside this
            generator aka the `with client.connect()` block.

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

    @contextmanager
    def connect_stream(self, callback):
        """Initiate a connection with the Theta Terminal Stream server on `localhost`.
        Requests can only be made inside this generator aka the `with client.connect_stream()` block.

        :raises ConnectionRefusedError: If the connection failed.
        :raises TimeoutError: If the timeout is set and has been reached.
        """

        try:
            for i in range(15):
                try:
                    self._stream_server = socket.socket()
                    self._stream_server.connect(("localhost", 10000))
                    self._stream_server.settimeout(1)
                    break
                except ConnectionError:
                    if i == 14:
                        raise ConnectionError('Unable to connect to the local Theta Terminal Stream process.'
                                              ' Try restarting your system.')
                    sleep(1)
            self._stream_server.settimeout(self.timeout)
            yield
            Thread(target=self._recv_stream(callback)).start()
        finally:
            self._stream_server.close()

    def req_full_trade_stream_opt(self):
        """from_bytes
          """
        assert self._stream_server is not None, _NOT_CONNECTED_MSG

        # send request
        hist_msg = f"MSG_CODE={MessageType.STREAM_REQ.value}&sec={SecType.OPTION.value}&req={OptionReqType.TRADE.value}\n"
        self._stream_server.sendall(hist_msg.encode("utf-8"))

    def req_trade_stream_opt(self, root: str, exp: date, strike: float, right: OptionRight):
        """from_bytes
          """
        assert self._stream_server is not None, _NOT_CONNECTED_MSG
        # format data
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)

        # send request
        hist_msg = f"MSG_CODE={MessageType.STREAM_REQ.value}&root={root}&exp={exp_fmt}&strike={strike}" \
                   f"&right={right.value}&sec={SecType.OPTION.value}&req={OptionReqType.TRADE.value}\n"
        self._stream_server.sendall(hist_msg.encode("utf-8"))

    def req_quote_stream_opt(self, root: str, exp: date, strike: float, right: OptionRight):
        """from_bytes
          """
        assert self._stream_server is not None, _NOT_CONNECTED_MSG
        # format data
        strike = _format_strike(strike)
        exp_fmt = _format_date(exp)

        # send request
        hist_msg = f"MSG_CODE={MessageType.STREAM_REQ.value}&root={root}&exp={exp_fmt}&strike={strike}" \
                   f"&right={right.value}&sec={SecType.OPTION.value}&req={OptionReqType.QUOTE.value}\n"
        self._stream_server.sendall(hist_msg.encode("utf-8"))

    def _recv_stream(self, callback):
        """from_bytes
          """
        msg = StreamMsg()
        parse_int = lambda d: int.from_bytes(d, "big")
        while True:
            msg.type = StreamMsgType.from_code(parse_int(self._read_stream(1)[:1]))
            msg.contract.from_bytes(self._read_stream(parse_int(self._read_stream(1)[:1])))

            if msg.type == StreamMsgType.QUOTE:
                msg.quote.from_bytes(self._read_stream(44))
            elif msg.type == StreamMsgType.TRADE:
                data = self._read_stream(n_bytes=32)
                msg.trade.from_bytes(data)
            else:
                continue
            callback(msg)

    def _read_stream(self, n_bytes: int) -> bytearray:
        """from_bytes
          """
        buffer = bytearray(self._stream_server.recv(n_bytes))
        total = buffer.__len__()

        while total < n_bytes:
            part = self._stream_server.recv(n_bytes - total)
            if part.__len__() < 0:
                continue
            total += part.__len__()
            buffer.extend(part)

        return buffer

    def _send_ver(self):
        """Sends this API version to the Theta Terminal."""
        ver_msg = f"MSG_CODE={MessageType.HIST.value}&version={_VERSION}\n"
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
        """Remotely kill the Terminal process. All subsequent requests will time out after this. A new instance of this
           class must be created.
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
         Get historical options data.

        :param req:            The request type.
        :param root:           The root / underlying / ticker / symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an option. CALL = Bullish; PUT = Bearish
        :param date_range:     The dates to fetch.
        :param interval_size:  The interval size in milliseconds. Applicable to most requests except ReqType.TRADE.
        :param use_rth:        If true, timestamps prior to 09:30 EST and after 16:00 EST will be ignored
                                  (only applicable to intervals requests).
        :param progress_bar:   Print a progress bar displaying download progress.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
         Returns the last tick at a provided millisecond of the day for a given request type.

        :param req:            The request type.
        :param root:           The root / underlying / ticker / symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an option. CALL = Bullish; PUT = Bearish
        :param date_range:     The dates to fetch.
        :param ms_of_day:      The time of day in milliseconds.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
         Returns the last tick at a provided millisecond of the day for a given request type.

        :param req:            The request type.
        :param root:           The root / underlying / ticker / symbol.
        :param date_range:     The dates to fetch.
        :param ms_of_day:      The time of day in milliseconds.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        :raises NoData:        If there is no data available for the request.
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
        :param root:           The root / underlying / ticker / symbol.

        :return:               All dates that Theta Data provides data for given a request.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        Get all dates of data available for a given options contract and request type.

        :param req:            The request type.
        :param root:           The root / underlying / ticker / symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.
        :param strike:         The strike price in USD.
        :param right:          The right of an options.

        :return:               All dates that Theta Data provides data for given a request.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        Get all dates of data available for a given options expiration and request type.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date. Must be after the start of `date_range`.

        :return:               All dates that Theta Data provides data for given options chain (expiration).
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        Get all options expirations for a provided underlying root.

        :param root:           The root / underlying / ticker / symbol.

        :return:               All expirations that ThetaData provides data for.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        out = f"MSG_CODE={MessageType.ALL_EXPIRATIONS.value}&root={root}\n"
        self._server.send(out.encode("utf-8"))
        header = Header.parse(out, self._server.recv(20))
        body = ListBody.parse(out, header, self._recv(header.size), dates=True)
        return body.lst

    def get_strikes(self, root: str, exp: date, date_range: DateRange = None,) -> pd.Series:
        """
        Get all options strike prices in US tenths of a cent.

        :param root:           The root / underlying / ticker / symbol.
        :param exp:            The expiration date.
        :param date_range:     If specified, this function will return strikes only if they have data for every
                                day in the date range.

        :return:               The strike prices on the expiration.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
        """
        assert self._server is not None, _NOT_CONNECTED_MSG
        assert isinstance(exp, date)
        exp_fmt = _format_date(exp)

        if date_range is not None:
            start_fmt = _format_date(date_range.start)
            end_fmt = _format_date(date_range.end)
            out = f"MSG_CODE={MessageType.ALL_STRIKES.value}&root={root}&exp={exp_fmt}&START_DATE={start_fmt}&END_DATE={end_fmt}\n"
        else:
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

        :return: All roots / underlyings / tickers / symbols for the security type.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        Get the most recent options tick.

        :param req:            The request type.
        :param root:           The root symbol.
        :param exp:            The expiration date.
        :param strike:         The strike price in USD, rounded to 1/10th of a cent.
        :param right:          The right of an options.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        :param root:           The root / underlying / ticker / symbol.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
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
        """
        Make a historical data request given the raw text output of a data request. Typically used for debugging.

        :param req:            The raw request.

        :return:               The requested data as a pandas DataFrame.
        :raises ResponseError: If the request failed.
        :raises NoData:        If there is no data available for the request.
        """
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

