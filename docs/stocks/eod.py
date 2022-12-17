import pandas as pd
from datetime import date
from thetadata import ThetaClient, DateRange, StockReqType


def end_of_day() -> pd.DataFrame:
    client = ThetaClient()  # No credentials required for free access

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        out = client.get_hist_stock(
            req=StockReqType.EOD,  # End of day data
            root="AAPL",
            date_range=DateRange(date(2022, 11, 14), date(2022, 11, 18))
        )
    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    data = end_of_day()
    print(data.to_string())
