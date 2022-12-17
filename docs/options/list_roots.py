import pandas as pd
from thetadata import ThetaClient, SecType


def get_roots() -> pd.Series:
    client = ThetaClient()  # No credentials required for free access

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        out = client.get_roots(sec=SecType.OPTION)

    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    roots = get_roots()
    print(roots)
