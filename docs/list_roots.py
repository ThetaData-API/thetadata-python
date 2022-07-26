import pandas as pd
from thetadata import ThetaClient, SecType


def get_roots() -> pd.Series:
    # Create a ThetaClient
    client = ThetaClient()

    # Connect to the Terminal
    with client.connect():

        # List all root symbols for options
        roots = client.get_roots(sec=SecType.OPTION)

    return roots


if __name__ == "__main__":
    roots = get_roots()
    print(roots)
