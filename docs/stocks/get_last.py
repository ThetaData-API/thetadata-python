import pandas as pd
from thetadata import ThetaClient, StockReqType


def get_last() -> pd.DataFrame:
    # Credentials now required because get_last is only available to ThetaData subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    # Make any requests for data inside this block. Requests made outside this block won't run.
    with client.connect():
        # Request the most recent quote for AAPL stock.
        out = client.get_last_stock(
            req=StockReqType.QUOTE,
            root="AAPL",
        )
    # We are out of the client.connect() block, so we can no longer make requests.
    return out


if __name__ == "__main__":
    quote = get_last()
    print(quote.to_string())
