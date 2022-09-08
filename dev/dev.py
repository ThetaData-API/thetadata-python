import pandas as pd
from datetime import date
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange


def eod() -> pd.DataFrame:
    # Create a ThetaClient
    client = ThetaClient(timeout=180)

    # Connect to the Terminal
    with client.connect():
        # Make the request
        out = client.get_hist_option(
                    req=OptionReqType.QUOTE,
                    root="AAPL",
                    exp=date(2022, 9, 16),
                    strike=140,
                    right=OptionRight.CALL,
                    date_range=DateRange(date(2022, 8, 31), date(2022, 8, 31)),
                    interval_size=60000,
                    progress_bar=False,
        )
        print(out)
        out = client.get_req("MSG_CODE=200&START_DATE=20220107&END_DATE=20220107&root=SPXW&exp=20220110&strike=4665000&right=P&sec=OPTION&req=104&IVL=60000")

    return out


if __name__ == "__main__":
    data = eod()
    print(data)
