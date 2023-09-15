import pandas as pd
from datetime import date
from thetadata import ThetaClient, DateRange, StockReqType


def quote() -> pd.DataFrame:
    # Credentials now required because get_last is only available to ThetaData subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        out = client.get_hist_stock(
            req=StockReqType.QUOTE,
            root="AMD",
            date_range=DateRange(date(2022, 11, 18), date(2022, 11, 18)),
        )

    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    data = quote()
    print(data.to_string(max_rows=8, max_cols=16))
