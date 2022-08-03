import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange


def end_of_day() -> pd.DataFrame:
    """Request end-of-day data between 7/18/2022 and 7/22/2022."""
    # Create a ThetaClient
    client = ThetaClient()

    # Connect to the Terminal
    with client.connect():

        # Make the request
        data = client.get_hist_option(
            req=OptionReqType.EOD,
            root="AAPL",
            exp=date(2022, 8, 12),
            strike=140,
            right=OptionRight.CALL,
            date_range=DateRange(date(2022, 7, 18), date(2022, 7, 22)),
        )

    return data


if __name__ == "__main__":
    data = end_of_day()
    print(data)
