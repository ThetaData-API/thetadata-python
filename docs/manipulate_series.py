import pandas as pd
from .stocks.list_roots import get_roots


def main():
    # get the result from the previous example
    roots: pd.Series = get_roots()

    # Check if a symbol is in the Series
    contains_apple = "AAPL" in roots.values

    # Count symbols
    count = len(roots)

    # Filter symbols to those that start with A
    filtered = [s for s in roots if s.startswith("A")]
    for symbol in filtered:
        # do something
        pass

    print(f"{contains_apple=}")
    print(f"{count=}")
    print(f"{len(filtered)=}")


if __name__ == "__main__":
    main()
