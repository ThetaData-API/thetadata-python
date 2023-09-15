import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionRight, DateRange, OptionReqType


def quote() -> pd.DataFrame:
    # Credentials now required because get_last is only available to ThetaData subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        out = client.get_hist_option(
            req=OptionReqType.QUOTE,
            root="AMD",
            exp=date(2022, 12, 16),
            strike=60,
            right=OptionRight.CALL,
            date_range=DateRange(date(2022, 11, 14), date(2022, 11, 18)),
        )
    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    data = quote()
    print(data.to_string(max_rows=8, max_cols=16))
