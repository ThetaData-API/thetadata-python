import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight


def get_last() -> pd.DataFrame:

    # Create a ThetaClient
    client = ThetaClient()

    # Connect to the Terminal
    with client.connect():

        # Request the most recent quote for AAPL
        quote = client.get_last_option(
            req=OptionReqType.QUOTE,
            root="AAPL",
            exp=date(2022, 9, 16),
            strike=140.00,
            right=OptionRight.CALL,
        )

    return quote


if __name__ == "__main__":
    quote = get_last()
    print(quote)
