# Quickstart

In this section you'll learn how to get started with thetadata and make simple requests.

## Installation

- Install Python 3.
- Install Java 11 or later. If you are using Windows, this will automatically be done for you. THIS IS REQUIRED TO USE THE API.
- Using pip, Python's package manager, open a terminal and run
`pip install thetadata`
or
`python -m pip install thetadata`

## Free data

### End of day stock data

With the API installed, you can now
`import thetadata` in any Python script you'd like!

Here's how you may make your first **free** stock data request:

=== "eod.py"

    ```python
    --8<-- "docs/stocks/eod.py"
    ```

=== "Output"

    ```bash
    > python eod.py                                                                                                                                                                         1 ✘ 
       DataType.OPEN  DataType.HIGH  DataType.LOW  DataType.CLOSE  DataType.VOLUME  DataType.COUNT DataType.DATE
    0         149.30       166.6500      135.3900         148.770         80889202          576303    2022-11-14
    1         149.51       153.5900      140.9150         149.700         96309849          703679    2022-11-15
    2         150.25       155.0800      138.9800         148.980         71463364          472255    2022-11-16
    3         149.08       159.0588      140.2858         150.865         86759251          563732    2022-11-17
    4         151.00       153.3400      134.8700         150.880         84146100          514111    2022-11-18
    ```

    > *What am I looking at?*

### End of day option data

Here's how you may make your first **free** option data request:

=== "eod.py"

    ```python
    --8<-- "docs/options/eod.py"
    ```

=== "Output"

    ```bash
    > python eod.py                                                                                                                                                                         1 ✘ 
       DataType.OPEN  DataType.HIGH  DataType.LOW  DataType.CLOSE  DataType.VOLUME  DataType.COUNT DataType.DATE
    0           5.50           6.15          4.75            5.10             8454            1155    2022-11-14
    1           6.40           8.10          5.45            5.95            14153            1476    2022-11-15
    2           5.42           5.84          4.55            5.15            10848             957    2022-11-16
    3           4.10           6.57          3.05            6.00             5820            1083    2022-11-17
    4           6.95           6.95          5.57            6.11             5553             951    2022-11-18
    ```

    > *What am I looking at?*

## List roots

A root can be defined as a unique identified for a stock / underlying asset. Common terms also
include: stock symbol, ticker, and underlying.

### Stock roots 
This request returns a series of all roots (stock symbols) that are available.

=== "list_roots.py"

    ```python
    --8<-- "docs/stocks/list_roots.py"
    ```

=== "Output"

    ```bash
    > python list_roots.py
    0         AAAP
    1         AABA
    2          AAC
    3         AACC
    4         AACG
         ...  
    9711    ZXYZ.A
    9712     ZXZZT
    9713        ZY
    9714      ZYNE
    9715      ZYXI
    Length: 9716, dtype: object
    ```


### Roots with options
This request returns a series of all roots (stock symbols) that have traded options.

=== "list_roots.py"

    ```python
    --8<-- "docs/options/list_roots.py"
    ```

=== "Output"

    ```bash
    > python list_roots.py
    0           A
    1          AA
    2        AADI
    3        AAIC
    4         AAL
            ...  
    6240     ZYXI
    6241    ZYXI1
    6242      ZZK
    6243      ZZZ
    6244     ZZZ1
    Length: 6245, dtype: object
    ```

Unlike historical data requests, `get_roots` returns a *Series*. In the pandas package, a
`Series` is a one-dimensional array, similar to a Python list.


## Understanding the output

The return type of any historical data request is a `DataFrame`, a core datatype 
in the **pandas** package. To understand what the `DataType` labels in the `DataFrame` mean,
please refer to our [request types page](https://www.thetadata.net/request-types).


> [pandas](https://pandas.pydata.org/) is a fast, powerful, flexible and easy to use open source data
> analysis and manipulation tool, built on top of the Python programming language.

The [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html)
covers significantly more material than this tutorial. However, a key takeaway is that
pandas operates on two data structures:

1. `Series`
2. `DataFrame`

A *Series* is a one-dimensional array, similar to a Python list. A *DataFrame* is a two-dimensional data structure with rows and columns, similar to a spreadsheet.

### Manipulating a `DataFrame`


The above example returned a `DataFrame`. Let's see how we can use it to process our data.

=== "manipulate_df.py"

    ```python
    --8<-- "docs/manipulate_df.py"
    ```

=== "Output"

    ```bash
    > python script.py
    Index([  DataType.OPEN,   DataType.HIGH,    DataType.LOW,  DataType.CLOSE,
       DataType.VOLUME,  DataType.COUNT,   DataType.DATE],
      dtype='object')
    close_price=149.3
    ```

    As you can see, the response contains 7 fields (DataFrame *columns*), and
    the close price of the first *row* of this data (which represents July 18, 2022) is $13.10.

Congratulations, you've processed your first request!

### Manipulating a `Series`

The above stock root list example returned a `Series`. Let's see how we can use it to 
process our data.

=== "manipulate_series.py"

    ```python
    --8<-- "docs/manipulate_series.py"
    ```

=== "Output"

    ```bash
    > python manipulate_series.py
    contains_apple=True
    count=9716
    len(filtered)=965
    ```

## Snapshots

A snapshot is the last quote / trade we have on record. Snapshots are best used when 
executing a trade. This allows you to determine the most recent price.

### 15-minute delayed stock snapshots

Currently, all of our equities data is 15 minutes delayed. We have plans to upgrade
to real-time equities feeds in the future. Below is an example of a stock snapshot:

=== "get_last_stk.py"

    ```python
    --8<-- "docs/stocks/get_last.py"
    ```

=== "Output"

    ```bash
    > python get_last.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0            61514177                  2                       7        134.37                      0                  3                       7        134.42                      0    2022-12-16
    ```


### Real-time option snapshots

Let's try a low-latency snapshot request for the most recent option quote available:

=== "get_last_opt.py"

    ```python
    --8<-- "docs/options/get_last.py"
    ```

=== "Output"

    ```bash
    > python get_last.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0            57599990                  1                       1          6.05                     50                 63                      46          6.55                     50    2022-12-16
    ```

## Historical NBBO Quotes

This tutorial will provide examples for requesting historical & intraday
[NBBO(National Best Bid & Offer)](https://www.investopedia.com/terms/n/nbbo.asp)
quotes.

### Preface

#### The `interval_size` parameter

We provide tick-level data for `QUOTE` requests. This means that when a request is made,
every single quote inside the`date_range` provided will be returned. This can end up being 
millions of quotes per trading day. Specifying the`interval_size` parameter aggregates these
quotes and provides the NBBO at every `interval_size` milliseconds.

#### Be careful!

Not specifying the `interval_size` will return tick-level data, which can be an obscene 
amount of data! If you plan to work with tick-level quote data, we recommend limiting 
your `date_range` (per-request) to 2 weeks for options and 1 day for stocks to prevent 
memory overflow errors. If you are using an `interval_size` >= `60000`(1-min), 
you shouldn't need to do this.

#### Why are there quotes with no bid or ask?

You'll notice that the first few quotes of the day may have empty bid and or ask and prices.
These are test quotes usually sent by exchanges or
[SIPs](https://www.investopedia.com/terms/n/national-market-system-plan.asp). It's safe
to ignore them. We maintain a policy of not filtering any data unless the user asks us to,
which is why they are included in tick-level requests.

### Stock Quotes

#### Tick-level NBBO quotes

The example below returns every NBBO quote that occurred on `2022-11-18` for `AMD` stock.
As seen in the output, there are over **5.8 million** quotes for this day alone, which is
why we recommend using a `date_range` of 1 for these requests.

=== "quote.py"

    ```python
    --8<-- "docs/stocks/quote_tick.py"
    ```

=== "Output"

    ```bash
    > python docs/stocks/quote_tick.py                                                                                                                                                                     
             DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0                  14340012                  0                       0          0.00                      0                  0                       0          0.00                      0    2022-11-18
    1                  14340126                  0                       0          0.00                      0                  0                       0          0.00                      0    2022-11-18
    2                  14400005                  4                       1         74.11                      0                  0                       0          0.00                      0    2022-11-18
    3                  14400005                  4                       1         74.11                      0                  4                       1         74.68                      0    2022-11-18
    ...                     ...                ...                     ...           ...                    ...                ...                     ...           ...                    ...           ...
    5894898            71998825                  8                      65         73.58                      0                  1                       7         73.58                      0    2022-11-18
    5894899            71998826                  8                      65         73.58                      0                  6                       7         73.60                      0    2022-11-18
    5894900            71998827                  8                      65         73.58                      0                  6                       7         73.60                      0    2022-11-18
    5894901            71998831                  8                      65         73.59                      0                  6                       7         73.60                      0    2022-11-18
    ```

#### 1-minute intervals NBBO quotes

The only difference from the example above is that we specify the ``interval_size``
parameter, which allows us to get the NBBO quote every minute of the trading day.
This significantly reduces output and improves latency.

=== "quote.py"

    ```python
    --8<-- "docs/stocks/quote_1min.py"
    ```

=== "Output"

    ```bash
    > python docs/stocks/quote_1min.py                                                                                                                                                                     
          DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0               34200000                  2                      65         75.23                      0                138                       1         75.24                      0    2022-11-14
    1               34260000                  1                       1         74.72                      0                  1                       1         74.77                      0    2022-11-14
    2               34320000                  1                      65         74.58                      0                  3                       7         74.60                      0    2022-11-14
    3               34380000                  2                      17         73.70                      0                  3                       7         73.71                      0    2022-11-14
    ...                  ...                ...                     ...           ...                    ...                ...                     ...           ...                    ...           ...
    1951            57420000                  5                       1         73.50                      0                  6                      63         73.51                      0    2022-11-18
    1952            57480000                  5                       3         73.48                      0                 12                       3         73.49                      0    2022-11-18
    1953            57540000                  7                       3         73.53                      0                 11                       3         73.54                      0    2022-11-18
    1954            57600000                209                       1         73.58                      0                314                       1         73.61                      0    2022-11-18
    ```

### Historical Option Quotes

#### Tick-level NBBO quotes

The example below returns every NBBO quote that occurred between `2022-11-14` and
`2022-11-18` for the `$60 AMD CALL` that expires on `2022-12-16`. As seen in the 
output, there are almost **1 million** quotes for this week alone, which is why we
recommend using a `date_range` of 2 weeks or fewer for tick-level option requests.

=== "quote.py"

    ```python
    --8<-- "docs/stocks/quote_1min.py"
    ```

=== "Output"

    ```bash
    > python docs/stocks/quote_1min.py                                                                                                                                                                     
        DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0                 28800107                  0                      65          0.00                     50                  0                      65          0.00                     50    2022-11-14
    1                 28801023                  0                       5          0.00                     50                  0                       5          0.00                     50    2022-11-14
    2                 28806116                  0                      42          0.00                     50                  0                      42          0.00                     50    2022-11-14
    3                 28806324                  0                      60          0.00                     50                  0                      60          0.00                     50    2022-11-14
    ...                    ...                ...                     ...           ...                    ...                ...                     ...           ...                    ...           ...
    979528            57598756               1183                       9         14.15                     50                 65                      11         14.45                     50    2022-11-18
    979529            57599253               1132                       9         14.15                     50                 65                      11         14.45                     50    2022-11-18
    979530            57599264               1118                       9         14.15                     50                 65                      11         14.45                     50    2022-11-18
    979531            57599539               1112                       9         14.15                     50                 65                      11         14.45                     50    2022-11-18
    ```

#### 1-minute intervals NBBO quotes

The only difference from the example above is that we specify the ``interval_size``
parameter, which allows us to get the NBBO quote every minute of the trading day.
This significantly reduces output and improves latency.

=== "quote.py"

    ```python
    --8<-- "docs/options/quote_1min.py"
    ```

=== "Output"

    ```bash
    > python docs/options/quote_1min.py                                                                                                                                                                        
          DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0               34200000                  0                      47          0.00                     50                  0                      47          0.00                     50    2022-11-14
    1               34260000               1081                       9         15.40                     50                188                      65         16.15                     50    2022-11-14
    2               34320000                151                       6         15.35                     50                 78                      11         15.85                     50    2022-11-14
    3               34380000                 40                      43         14.75                     50                138                      43         15.10                     50    2022-11-14
    ...                  ...                ...                     ...           ...                    ...                ...                     ...           ...                    ...           ...
    1946            57360000               2021                       9         14.15                     50                 77                      43         14.35                     50    2022-11-18
    1947            57420000               2056                       9         14.15                     50                 39                      47         14.35                     50    2022-11-18
    1948            57480000               2123                       9         14.15                     50                 63                      11         14.35                     50    2022-11-18
    1949            57540000               1887                       9         14.15                     50                 87                      11         14.40                     50    2022-11-18
    ```


## What's next?

Nice! You are now familiar the `Series` and `DataFrame` objects, the return types of our data requests.
Using the skills learned in this tutorial, you're well on your way to mastering the entire `thetadata` package.
Explore other requests at your disposal on the API Reference page!

For more details on the `pandas` API, please see the [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html).

