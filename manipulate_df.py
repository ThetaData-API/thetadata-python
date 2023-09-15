import pandas as pd
from thetadata import DataType
from .stocks.eod import end_of_day


def main():
    # get the data from the previous EOD stock data example
    data: pd.DataFrame = end_of_day()

    # print all datatypes in the response
    print(f"{data.columns}")

    # get the first row in the DataFrame (our requested data)
    row = data.iloc[0]

    # print just the open price
    open_price = row[DataType.OPEN]
    print(f"{open_price=}")


if __name__ == "__main__":
    main()
