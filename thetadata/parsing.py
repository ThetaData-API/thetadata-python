"""Module that parses data from the Terminal."""
from __future__ import annotations
from tqdm import tqdm

from dataclasses import dataclass
import pandas as pd
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
        parse_int = lambda d: int.from_bytes(d, "big")

        # parse ticks
        n_ticks = int(header.size / (header.format_len * 4))
        bytes_per_tick = header.format_len

        # parse format tick
        format_tick_codes = []
        for b in range(bytes_per_tick):
            int_ = parse_int(data[b * 4 : b * 4 + 4])
            format_tick_codes.append(int_)
        format: list[_DataType] = list(
            map(lambda code: _DataType.from_code(code), format_tick_codes)
        )

        # initialize empty dataframe w/ format columns
        df = pd.DataFrame(columns=format)

        # get the index of the price type column if it exists
        price_type_idx = None
        if _DataType.PRICE_TYPE in df.columns:
            price_type_idx = df.columns.get_loc(_DataType.PRICE_TYPE)

        # parse the rest of the ticks
        ticks = []
        for tn in tqdm(
            range(1, n_ticks), desc="Processing", disable=not progress_bar
        ):
            tick_offset = tn * bytes_per_tick * 4
            tick = []
            for b in range(bytes_per_tick):
                # parse int
                int_offset = tick_offset + b * 4
                int_ = parse_int(data[int_offset : int_offset + 4])
                tick.append(int_)

            # map price columns to prices if the tick contains a price type
            if price_type_idx is not None:
                # get price multiplier from price type
                pt = tick[price_type_idx]
                price_multiplier = _pt_to_price_mul[pt]
                # multiply tick price fields by price multiplier
                for i in range(len(tick)):
                    if format[i].is_price():
                        tick[i] = tick[i] * price_multiplier
                # remove price type from tick
                del tick[price_type_idx]

            ticks.append(tick)

        # delete price type column if it exists
        if price_type_idx is not None:
            del df[_DataType.PRICE_TYPE]

        # add ticks to dataframe in a single concat
        df = pd.concat(
            [pd.DataFrame(ticks, columns=df.columns), df],
            ignore_index=True,
        )

        return cls(ticks=df)


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
