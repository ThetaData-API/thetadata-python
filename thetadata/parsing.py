"""Module that parses data from the Terminal."""
from __future__ import annotations
from typing import Optional

from tqdm import tqdm

from dataclasses import dataclass
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from .exceptions import ResponseError, NoData, ResponseParseError, ReconnectingToServer
from .enums import DataType, MessageType


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
    def parse(cls, request: str, data: bytes) -> Header:
        """Parse binary header data into an object.

        :param request: the request that returned the header data
        :param data: raw header data, 20 bytes long
        :raises ResponseParseError: if parsing failed
        """
        try:
            return cls._parse(data)
        except Exception as e:
            raise ResponseParseError(
                f"Failed to parse header for request: {request}. Please send this error to support."
            ) from e

    @classmethod
    def _parse(cls, data: bytes) -> Header:
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

    :raises NoData: if the server does not contain data for the request.
    :raises ReconnectingToServer: if the connection has been lost to Theta Data and a
                                  reconnection attempt is being made/
    :raises ResponseError: if the header indicates an error, containing a
                           helpful error message.
    """
    if header.message_type == MessageType.ERROR:
        msg = body_data.decode("utf-8")
        if "no data" in msg.lower():
            raise NoData(msg)
        elif "disconnected" in msg.lower():
            raise ReconnectingToServer(msg)
        else:
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

# Vectorized function that maps price types to price multipliers
_to_price_mul = np.vectorize(lambda pt: _pt_to_price_mul[pt], otypes=[float])


class TickBody:
    """Represents the body returned on Terminal calls that deal with ticks."""

    def __init__(self, format_tick: list[DataType], body_ticks: np.ndarray):
        assert isinstance(format_tick, list) and isinstance(
            body_ticks, np.ndarray
        ), "Cannot initialize body bc ticks is not a DataFrame"
        self.format_tick: list[DataType] = format_tick
        self.body_ticks: np.ndarray = body_ticks

    @classmethod
    def parse(cls, request: str, header: Header, data: bytearray) -> DataFrame:
        """Efficiently parse binary tick data.

        :param request: the request that returned the body data
        :param header: parsed header data
        :param data: the binary response body
        :return: a processed pandas dataframe
        :raises ResponseParseError: if parsing failed
        """
        assert isinstance(
            data, bytearray
        ), f"Expected data to be bytearray type. Got {type(data)}"
        _check_body_errors(header, data)
        try:
            tbody = cls._parse(header, data)
            df = tbody._to_dataframe()
            return df
        except Exception as e:
            raise ResponseParseError(
                f"Failed to parse body for request: {request}. Please send this error to support."
            ) from e

    @classmethod
    def _parse(cls, header: Header, data: bytearray) -> TickBody:
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        n_cols = header.format_len
        n_ticks = int(header.size / (header.format_len * 4))

        # parse format tick
        format: list[DataType] = []
        for ci in range(n_cols):
            int_ = int.from_bytes(data[ci * 4 : ci * 4 + 4], "big")
            format.append(DataType.from_code(int_))

        # parse the rest of the ticks
        # 4 byte integers w/ big endian order
        dtype = np.dtype("int32").newbyteorder(">")
        ticks = (
            np.frombuffer(data, dtype=dtype, offset=(header.format_len * 4))
            .reshape((n_ticks - 1), n_cols)
            .byteswap()  # force native byte order
            .newbyteorder()  # ^^
        )

        return cls(format_tick=format, body_ticks=ticks)

    def _to_dataframe(self) -> DataFrame:
        """Load this tick data into a pandas DataFrame and post process.

        Post-processing modifies the columns of data w/ various quality-of-life
        improvements.
        """
        # load ticks into DataFrame
        df = pd.DataFrame(
            self.body_ticks, columns=self.format_tick, copy=False
        )
        self._post_process(df)
        return df

    @classmethod
    def _post_process(cls, df: DataFrame) -> None:
        """Modify tick data w/ various quality-of-life improvements.

        :param df: The DataFrame to modify in-place.
        """
        # remove trailing null tick if it exists
        last_row = df.tail(1)
        zeroes = last_row.squeeze() == 0
        if zeroes.all():
            # print(f"Dropping {last_row=}")
            df.drop(last_row.index, inplace=True)

        if DataType.PRICE_TYPE in df.columns:
            # replace price type column with price multipliers

            df[DataType.PRICE_TYPE] = _to_price_mul(df[DataType.PRICE_TYPE])

            # multiply prices by price multipliers
            for col in df.columns:
                if col.is_price():
                    df[col] *= df[DataType.PRICE_TYPE]

            # remove price type column
            del df[DataType.PRICE_TYPE]

        # convert date ints to datetime
        if DataType.DATE in df.columns:
            df[DataType.DATE] = pd.to_datetime(
                df[DataType.DATE], format="%Y%m%d"
            )


class ListBody:
    """Represents the body returned on every Terminal call that have one DataType."""

    def __init__(self, lst: Series):
        assert isinstance(
            lst, Series
        ), "Cannot initialize body bc lst is not a Series"
        self.lst: Series = lst

    @classmethod
    def parse(
        cls, request: str, header: Header, data: bytes, dates: bool = False
    ) -> ListBody:
        """Parse binary body data into an object.

        :param request: the request that returned the header data
        :param header: parsed header data
        :param data: the binary response body
        :param dates: whether to parse the data as date objects
        :raises ResponseParseError: if parsing failed
        """
        _check_body_errors(header, data)
        try:
            return cls._parse(header, data, dates)
        except Exception as e:
            raise ResponseParseError(
                f"Failed to parse header for request: {request}. Please send this error to support."
            ) from e

    @classmethod
    def _parse(
        cls, header: Header, data: bytes, dates: bool = False
    ) -> ListBody:
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."

        lst = data.decode("ascii").split(",")
        lst = pd.Series(lst, copy=False)

        if dates:
            lst = pd.to_datetime(lst, format="%Y%m%d")

        return cls(lst=lst)
