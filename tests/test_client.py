"""Contains various tests for the ThetaClient class."""
import pytest
import datetime
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange


@pytest.fixture
def tc():
    """Generate a ThetaClient connected to the Terminal."""
    client = ThetaClient(timeout=10)
    with client.connect():
        yield client


def test_hist_options(tc: ThetaClient):
    """Test a historical option request."""
    req = OptionReqType.QUOTE
    root = "BDX"
    exp = datetime.date(2022, 7, 1)
    strike = 240000
    right = OptionRight.CALL
    interval = 100
    date_range = DateRange.from_days(100)
    tc.get_hist_option(req, root, exp, strike, right, interval, date_range)
