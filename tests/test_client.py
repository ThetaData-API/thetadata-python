"""Contains various tests for the ThetaClient class."""
import pytest
import datetime
import thetadata
from thetadata import (
    ThetaClient,
    OptionReqType,
    OptionRight,
    DateRange,
    SecType,
    DataType,
)
import pandas as pd
from pandas import DataFrame, Series


@pytest.fixture
def tc():
    """Generate a ThetaClient connected to the Terminal."""
    client = ThetaClient(timeout=15)
    with client.connect():
        yield client


def test_hist_options(tc: ThetaClient):
    """Test a historical option request."""
    res = tc.get_hist_option(
        req=OptionReqType.QUOTE,
        root="BDX",
        exp=datetime.date(2022, 7, 1),
        strike=240000,
        right=OptionRight.CALL,
        date_range=DateRange.from_days(30),
        progress_bar=True,
    )
    print(res)
    print(res.columns)
    assert isinstance(res, DataFrame)
    assert len(res) > 0


def test_hist_options_large(tc: ThetaClient):
    """Test a very large historical option request."""
    res = tc.get_hist_option(
        req=OptionReqType.QUOTE,
        root="AAPL",
        exp=datetime.date(2022, 7, 1),
        strike=140000,
        right=OptionRight.CALL,
        date_range=DateRange(
            datetime.date(2022, 7, 4), datetime.date(2022, 7, 8)
        ),
        progress_bar=True,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res) > 0


def test_get_expirations(tc: ThetaClient):
    """Test an expirations listing request."""
    res = tc.get_expirations(root="BDX")
    print(res)
    assert isinstance(res, Series)
    assert len(res) > 0


def test_get_strikes_error(tc: ThetaClient):
    """Ensure that an invalid strike listing request raises."""
    with pytest.raises(thetadata.ResponseError) as e_info:
        res = tc.get_strikes(root="BDX", exp="20220601")


def test_get_strikes(tc: ThetaClient):
    """Test a strike listing request."""
    res = tc.get_strikes(root="AAPL", exp="20220429")
    print(res)
    assert isinstance(res, Series)
    assert len(res) > 0


def test_get_roots(tc: ThetaClient):
    """Test a root listing request."""
    res = tc.get_roots(sec=SecType.OPTION)
    print(res)
    assert isinstance(res, Series)
    assert len(res) > 0


@pytest.mark.skip(reason="Response is a WIP - still needs format tick")
def test_get_last(tc: ThetaClient):
    """Test a get last option data request."""
    res = tc.get_last_option(
        root="BDX",
        exp=datetime.date(2022, 7, 1),
        strike=240000,
        right=OptionRight.CALL,
    )
    print(res)
    assert isinstance(res, DataFrame)
    assert len(res) == 1
