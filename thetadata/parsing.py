"""Module that parses data from the Terminal."""
from __future__ import annotations
from typing import Optional

from tqdm import tqdm

from dataclasses import dataclass
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from .exceptions import ResponseError
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
    def parse(cls, data: bytes) -> Header:
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

    :raises ResponseError: if the header indicates an error, containing a
                           helpful error message.
    """
    if header.message_type == MessageType.ERROR:
        msg = body_data.decode("ascii")
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

    def __init__(self, ticks: DataFrame):
        assert isinstance(
            ticks, DataFrame
        ), "Cannot initialize body bc ticks is not a DataFrame"
        self.ticks: DataFrame = ticks

    @classmethod
    def parse(cls, header: Header, data: bytearray) -> TickBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        assert isinstance(
            data, bytearray
        ), f"Expected data to be bytearray type. Got {type(data)}"
        _check_body_errors(header, data)

        n_cols = header.format_len
        n_ticks = int(header.size / (header.format_len * 4))

        # parse format tick
        format_tick_codes = []
        for ci in range(n_cols):
            int_ = int.from_bytes(data[ci * 4 : ci * 4 + 4], "big")
            format_tick_codes.append(int_)
        format: list[DataType] = list(
            map(lambda code: DataType.from_code(code), format_tick_codes)
        )

        # initialize empty dataframe w/ format columns
        df = pd.DataFrame(columns=format)

        # parse the rest of the ticks
        # 4 byte integers w/ big endian order
        dtype = np.dtype("int32").newbyteorder(">")
        ticks = (
            np.frombuffer(data, dtype=dtype, offset=(header.format_len * 4))
            .reshape((n_ticks - 1), n_cols)
            .byteswap()  # force native byte order
            .newbyteorder()  # ^^
        )

        # load ticks into DataFrame
        df = pd.DataFrame(ticks, columns=df.columns, copy=False)
        cls._post_process(df)

        return cls(ticks=df)

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
    def parse(cls, header: Header, data: bytes) -> ListBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        _check_body_errors(header, data)

        lst = data.decode("ascii").split(",")
        lst = pd.Series(lst, copy=False)

        return cls(lst=lst)
