"""Contains various tests for the ThetaClient class."""
import pytest
from thetadata import ThetaClient


@pytest.fixture
def tc():
    """Generate a ThetaClient connected to the Terminal."""
    client = ThetaClient()
    print("hi")
    with client.connect():
        print("hi")
        yield client


def test_ping(tc: ThetaClient):
    """Test the ping request."""
    tc.ping()
