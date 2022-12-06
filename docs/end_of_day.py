import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange


def end_of_day() -> pd.DataFrame:

    client = ThetaClient()  # No credentials required for free access

    with client.connect():  # Make any requests for data inside this block. Requests made outside this block won't run.
        # Make the request
        data = client.get_hist_option(
            req=OptionReqType.EOD,
            root="AAPL",
            exp=date(2022, 11, 25),
            strike=150,
            right=OptionRight.CALL,
            date_range=DateRange(date(2022, 10, 15), date(2022, 11, 15))
        )
    # We are out of the client.connect() block, so we can no longer make requests.
    print(data)


if __name__ == "__main__":
    data = end_of_day()
    print(data)
