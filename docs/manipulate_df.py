import pandas as pd
from thetadata import DataType
from .first_request import first_request


def main():
    # get the quote from the previous example
    quote: pd.DataFrame = first_request()

    # print all datatypes in the response
    print(f"{quote.columns}")

    # get the first row in the DataFrame (our requested data)
    row = quote.iloc[0]

    # print just the bid price
    bid_price = row[DataType.BID]
    print(f"{bid_price=}")


if __name__ == "__main__":
    main()
