import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight


def get_last() -> pd.DataFrame:
    # Credentials now required because get_last is only available to ThetaData subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        # Request the most recent quote for an AAPL $130.00 CALL options expiring on 2022-12-30.
        out = client.get_last_option(
            req=OptionReqType.QUOTE,
            root="AAPL",
            exp=date(2022, 12, 30),
            strike=130.00,
            right=OptionRight.CALL,
        )
    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    quote = get_last()
    print(quote.to_string())
