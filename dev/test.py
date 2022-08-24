

import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange

from thetadata.terminal import launch_terminal, check_download


def end_of_day() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180)

    # Connect to the Terminal
    with client.connect():

        # Make the request
        data = client.get_hist_option(
            req=OptionReqType.EOD,
            root="AAPL",
            exp=date(2022, 8, 12),
            strike=160,
            right=OptionRight.CALL,
            date_range=DateRange(date(2022, 8, 3), date(2022, 8, 3)),
            progress_bar=True,
        )

    return data


if __name__ == "__main__":
    data = end_of_day()
    print(data)


