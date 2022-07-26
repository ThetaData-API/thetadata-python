import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight


def first_request() -> pd.DataFrame:

    # Create a ThetaClient
    client = ThetaClient()

    # Connect to the Terminal
    with client.connect():

        # Request the most recent quote for AAPL
        quote = client.get_last_option(
            req=OptionReqType.QUOTE,
            root="AAPL",
            exp=date(2022, 8, 12),
            strike=140.00,
            right=OptionRight.CALL,
        )

    return quote


if __name__ == "__main__":
    quote = first_request()
    print(quote)
