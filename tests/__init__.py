"""Package containing tests for the ThetaData Python API."""
import pytest
from thetadata import ThetaClient


@pytest.fixture
def tc():
    """Generate a ThetaClient connected to the Terminal."""
    client = ThetaClient(timeout=15, launch=False)
    with client.connect():
        yield client
