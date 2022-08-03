import pandas as pd
from thetadata import DataType
from .end_of_day import end_of_day


def main():
    # get the data from the previous example
    data: pd.DataFrame = end_of_day()

    # print all datatypes in the response
    print(f"{data.columns}")

    # get the first row in the DataFrame (our requested data)
    row = data.iloc[0]

    # print just the close price
    close_price = row[DataType.CLOSE]
    print(f"{close_price=}")


if __name__ == "__main__":
    main()
