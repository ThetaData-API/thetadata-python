import pandas as pd
from datetime import date

import thetadata.exceptions
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange, DataType


def strikes_crash() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180, username="baileydan911@gmail.com", passwd="ihatelag911bq")

    # Connect to the Terminal
    with client.connect():

        exp = date(2022, 1, 10)

        strikes = client.get_strikes("SPXW", exp)
        # Make the request
        data = None

        for j in strikes:
            try:
                data = client.get_hist_option(
                    req=OptionReqType.QUOTE,
                    root="SPXW",
                    exp=date(2022, 1, 10),
                    strike=int(j) / 1000.0,
                    right=OptionRight.CALL,
                    date_range=DateRange(date(2022, 1, 6), date(2022, 1, 7)),
                    interval_size=60000,
                    progress_bar=False,
                )

                data = client.get_hist_option(
                    req=OptionReqType.OHLC,
                    root="SPXW",
                    exp=date(2022, 1, 10),
                    strike=int(j) / 1000.0,
                    right=OptionRight.CALL,
                    date_range=DateRange(date(2022, 1, 6), date(2022, 1, 7)),
                    interval_size=60000,
                    progress_bar=False,
                )
                print('found')
            except thetadata.exceptions.NoData:
                print("no data for exp: " + str(exp) + " strike: " + str(int(j) / 1000.0))

    return data


def crash() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180, username="baileydan911@gmail.com", passwd="ihatelag911bq")

    # Connect to the Terminal
    with client.connect():
        # Make the request
        data = client.get_hist_option(
            req=OptionReqType.OHLC,
            root="SPY",
            exp=date(2022, 8, 26),
            strike=410,
            right=OptionRight.PUT,
            date_range=DateRange(date(2022, 8, 25), date(2022, 8, 26)),
            interval_size=60000,
        )

    return data


if __name__ == "__main__":
    out = crash()
    print(out)
