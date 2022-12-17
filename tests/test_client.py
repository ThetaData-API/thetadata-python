"""Contains various tests for the ThetaClient class."""
import warnings

import pandas as pd
from pandas import DataFrame, Series
import pytest
import datetime
import thetadata
from thetadata import (
    ThetaClient,
    OptionReqType,
    OptionRight,
    DateRange,
    SecType,
    DataType, NoData,
)
from . import tc


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_end_of_day(tc: ThetaClient):
    """Test an EOD historical request."""
    res = tc.get_hist_option(
        req=OptionReqType.EOD,
        root="AAPL",
        exp=datetime.date(2022, 7, 15),
        strike=140,
        right=OptionRight.CALL,
        date_range=DateRange(
            datetime.date(2022, 7, 6), datetime.date(2022, 7, 15)
        ),
        progress_bar=True,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_hist_option_quotes_small(tc: ThetaClient):
    """Test a historical options request."""
    res = tc.get_hist_option(
        req=OptionReqType.QUOTE,
        root="AAPL",
        exp=datetime.date(2022, 7, 15),
        strike=140,
        right=OptionRight.CALL,
        date_range=DateRange(
            datetime.date(2022, 7, 6), datetime.date(2022, 7, 8)
        ),
        progress_bar=True,
    )
    print(res)
    print(res.columns)
    assert isinstance(res, DataFrame)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_hist_option_quotes_large(tc: ThetaClient):
    """Test a very large historical options request."""
    res = tc.get_hist_option(
        req=OptionReqType.QUOTE,
        root="AAPL",
        exp=datetime.date(2022, 7, 15),
        strike=140,
        right=OptionRight.CALL,
        date_range=DateRange(
            datetime.date(2022, 7, 4), datetime.date(2022, 7, 8)
        ),
        progress_bar=True,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_hist_option_trades(tc: ThetaClient):
    """Test a very large historical options request."""
    res = tc.get_hist_option(
        req=OptionReqType.TRADE,
        root="AAPL",
        exp=datetime.date(2022, 9, 16),
        strike=140,
        right=OptionRight.CALL,
        date_range=DateRange(datetime.date(2022, 9, 1), datetime.date(2022, 9, 16)),
        progress_bar=True,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_hist_option_open_interest(tc: ThetaClient):
    """Test a very large historical options request."""
    today = datetime.date.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7)
    print("exp:        " + friday.__str__())
    print("root:       " + "AAPL")
    print("Date range: " + DateRange.from_days(7).__str__())

    try:
        res = tc.get_hist_option(
            req=OptionReqType.OPEN_INTEREST,
            root="AAPL",
            exp=datetime.date(2022, 11, 11),
            strike=140,
            right=OptionRight.CALL,
            date_range=DateRange(start=datetime.date(2022, 10, 29), end=datetime.date(2022, 11, 5)),
            progress_bar=True,
        )
    except NoData:
        today = datetime.date.today() + datetime.timedelta(days=7)
        friday = today + datetime.timedelta((4 - today.weekday()) % 7)
        res = tc.get_hist_option(
            req=OptionReqType.OPEN_INTEREST,
            root="AAPL",
            exp=friday,
            strike=140,
            right=OptionRight.CALL,
            date_range=DateRange.from_days(7),
            progress_bar=True,
        )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_get_expirations(tc: ThetaClient):
    """Test an expirations listing request."""
    res = tc.get_expirations(root="AAPL")
    print(res)
    assert isinstance(res, Series)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_get_strikes_error(tc: ThetaClient):
    """Ensure that an invalid strike listing request raises."""
    with pytest.raises(thetadata.ResponseError) as e_info:
        res = tc.get_strikes(root="BDX", exp=datetime.date(2022, 6, 1))


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_get_strikes(tc: ThetaClient):
    """Test a strike listing request."""
    res = tc.get_strikes(
        root="AAPL",
        exp=datetime.date(2022, 7, 29),
    )
    print(res)
    assert isinstance(res, Series)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Ignore for now.")  # TODO: remove
def test_get_roots(tc: ThetaClient):
    """Test a root listing request."""
    res = tc.get_roots(sec=SecType.OPTION)
    print(res)
    assert isinstance(res, Series)
    assert len(res.index) > 0


@pytest.mark.skip(reason="Unable to retrieve last Price")  # TODO: remove
def test_get_last(tc: ThetaClient):
    """Test a get last options data request."""
    res = tc.get_last_option(
        req=OptionReqType.QUOTE,
        root="AAPL",
        exp=(datetime.datetime.now() + datetime.timedelta(days=4)).date(),
        strike=140,
        right=OptionRight.CALL,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res.index) == 1


@pytest.mark.skip(reason="Cannot automate restart yet")
def test_kill_method(tc: ThetaClient):
    """Test killing the Terminal process by calling client.kill()"""
    tc.kill()
