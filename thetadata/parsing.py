"""Module that parses data from the Terminal."""
from __future__ import annotations
from typing import Optional

from tqdm import tqdm

from dataclasses import dataclass
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from .exceptions import ResponseError
from .enums import _DataType, MessageType


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


class TickBody:
    """Represents the body returned on Terminal calls that deal with ticks."""

    def __init__(self, ticks: DataFrame):
        assert isinstance(
            ticks, DataFrame
        ), "Cannot initialize body bc ticks is not a DataFrame"
        self.ticks: DataFrame = ticks

    @classmethod
    def parse(
        cls, header: Header, data: bytes, progress_bar: bool = False
    ) -> TickBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        :param: progress_bar: Print a progress bar displaying progress.
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        _check_body_errors(header, data)

        # avoid copying body data when slicing
        data = memoryview(data)

        # parse ticks
        n_cols = header.format_len
        n_ticks = int(header.size / (header.format_len * 4))

        # parse format tick
        format_tick_codes = []
        for ci in range(n_cols):
            int_ = int.from_bytes(data[ci * 4 : ci * 4 + 4], "big")
            format_tick_codes.append(int_)
        format: list[_DataType] = list(
            map(lambda code: _DataType.from_code(code), format_tick_codes)
        )

        # initialize empty dataframe w/ format columns
        df = pd.DataFrame(columns=format)

        try:
            price_type_idx = df.columns.get_loc(_DataType.PRICE_TYPE)
        except KeyError:
            price_type_idx = None

        # parse the rest of the ticks
        ticks = np.empty((n_ticks, n_cols))
        # TODO: multithread processing
        for tn in tqdm(
            range(1, n_ticks), desc="Processing", disable=not progress_bar
        ):
            # the first byte of the tnth tick
            tick_offset = tn * n_cols * 4
            tick = np.empty(n_cols)
            for ci in range(n_cols):
                # parse int
                int_offset = tick_offset + ci * 4
                int_ = int.from_bytes(data[int_offset : int_offset + 4], "big")
                # map price types to price multipliers
                tick[ci] = (
                    _pt_to_price_mul[int_]
                    if price_type_idx is not None and price_type_idx == ci
                    else int_
                )

            ticks[tn - 1] = tick

        # load ticks into DataFrame
        df = pd.DataFrame(ticks, columns=df.columns, copy=False)
        cls._post_process(df)

        return cls(ticks=df)

    @classmethod
    def _post_process(cls, df: DataFrame) -> None:
        """Modify tick data w/ various quality-of-life improvements.

        :param df: The DataFrame to modify in-place.
        """
        if _DataType.PRICE_TYPE in df.columns:
            # multiply prices by price multipliers
            for col in df.columns:
                if col.is_price():
                    df[col] *= df[_DataType.PRICE_TYPE]

            # remove price type column
            del df[_DataType.PRICE_TYPE]


class ListBody:
    """Represents the body returned on every Terminal call that have one DataType."""

    def __init__(self, lst: Series):
        assert isinstance(
            lst, Series
        ), "Cannot initialize body bc lst is not a Series"
        self.lst: Series = lst

    @classmethod
    def parse(
        cls, header: Header, data: bytes, progress_bar: bool = False
    ) -> ListBody:
        """Parse binary body data into an object.

        :param header: parsed header data
        :param data: the binary response body
        :param: progress_bar: Print a progress bar displaying progress.
        """
        assert (
            len(data) == header.size
        ), f"Cannot parse body with {len(data)} bytes. Expected {header.size} bytes."
        _check_body_errors(header, data)

        lst = data.decode("ascii").split(",")
        lst = pd.Series(lst, copy=False)

        return cls(lst=lst)
