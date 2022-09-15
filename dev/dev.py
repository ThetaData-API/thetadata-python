import os

import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange


def eod() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180, username="baileydan911@gmail.com", passwd="ihatelag911bq")

    # Connect to the Terminal
    with client.connect():
        # Make the request
        data = client.get_hist_option(
            req=OptionReqType.EOD,
            root="AAPL",
            exp=date(2022, 9, 30),
            strike=160,
            right=OptionRight.CALL,
            date_range=DateRange(date(2022, 8, 22), date(2022, 8, 22)),
            interval_size=60000
        )

    return data


if __name__ == "__main__":
    eod()