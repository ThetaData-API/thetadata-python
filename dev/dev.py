import pandas as pd
from datetime import date

import thetadata.exceptions
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange, DataType


def strikes_crash() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180)

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
    client = ThetaClient()

    # Connect to the Terminal
    with client.connect():
        with open("raw.txt") as f:
            # Make the request
            s = f.readline()
            count = 0

            while s is not None:
                try:
                    if count == 109:
                        data = client.get_req(s)
                except thetadata.NoData:
                    x = 0
                count += 1
                s = f.readline()
    return data


if __name__ == "__main__":
    out = crash()
