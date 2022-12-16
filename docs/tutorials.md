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

### Get end of day stock data

With the API installed, you can now
`import thetadata` in any Python script you'd like!

Here's how you may make your first **free** stock data request:

=== "end_of_day_stk.py"

    ```python
    --8<-- "docs/end_of_day_stk.py"
    ```

=== "Output"

    ```bash
    > python end_of_day_stk.py                                                                                                                                                                         1 ✘ 
       DataType.OPEN  DataType.HIGH  DataType.LOW  DataType.CLOSE  DataType.VOLUME  DataType.COUNT DataType.DATE
    0         149.30       166.6500      135.3900         148.770         80889202          576303    2022-11-14
    1         149.51       153.5900      140.9150         149.700         96309849          703679    2022-11-15
    2         150.25       155.0800      138.9800         148.980         71463364          472255    2022-11-16
    3         149.08       159.0588      140.2858         150.865         86759251          563732    2022-11-17
    4         151.00       153.3400      134.8700         150.880         84146100          514111    2022-11-18
    ```

    > *What am I looking at?*

### Get end of day option data

Here's how you may make your first **free** option data request:

=== "end_of_day_opt.py"

    ```python
    --8<-- "docs/end_of_day_opt.py"
    ```

=== "Output"

    ```bash
    > python end_of_day_opt.py                                                                                                                                                                         1 ✘ 
       DataType.OPEN  DataType.HIGH  DataType.LOW  DataType.CLOSE  DataType.VOLUME  DataType.COUNT DataType.DATE
    0           5.50           6.15          4.75            5.10             8454            1155    2022-11-14
    1           6.40           8.10          5.45            5.95            14153            1476    2022-11-15
    2           5.42           5.84          4.55            5.15            10848             957    2022-11-16
    3           4.10           6.57          3.05            6.00             5820            1083    2022-11-17
    4           6.95           6.95          5.57            6.11             5553             951    2022-11-18
    ```

    > *What am I looking at?*

## Understanding the output

The return type of any historical data request is a `DataFrame`, a core datatype 
in the **pandas** package. To understand what the `DataType` labels in the `DataFrame` mean,
please refer to our [request types page](https://www.thetadata.net/request-types)

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
    open_price=149.3
    ```

    As you can see, the response contains 7 fields (DataFrame *columns*), and
    the open price of the first *row* of this data (which represents November 14th, 2022) is $149.30.

Congratulations, you've made and processed your first request!

## List roots

A root can be defined as a unique identified for a stock / underlying asset. Common terms also
include: stock symbol, ticker, and underlying.

### List stock roots 
This request returns a series of all roots (stock symbols) that are available.

=== "list_roots.py"

    ```python
    --8<-- "docs/list_roots_stk.py"
    ```

=== "Output"

    ```bash
    > python list_roots_stk.py
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


### List roots with options
This request returns a series of all roots (stock symbols) that have traded options.

=== "list_roots.py"

    ```python
    --8<-- "docs/list_roots_opt.py"
    ```

=== "Output"

    ```bash
    > python list_roots_opt.py
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

Unlike the previous request, `get_roots` returns a *Series*. In the pandas package, a
`Series` is a one-dimensional array, similar to a Python list.

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

## What's next?

Nice! You are now familiar the `Series` and `DataFrame` objects, the return types of our data requests.
Using the skills learned in these tutorials, you're well on your way to mastering the entire `thetadata` package.
Explore other requests at your disposal on the API Reference page!

For more details on the `pandas` API, please see the [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html).


# Snapshots

A snapshot is the last quote / trade we have on record. Snapshots are bested used when 
executing a trade. This allows you to determine the most recent price.

## 15-minute delayed stock snapshots

Currently, all of our equities data is 15 minutes delayed. We have plans to upgrade
to real-time equities feeds in the future. Below is an example of a stock snapshot:

=== "get_last_stk.py"

    ```python
    --8<-- "docs/get_last_stk.py"
    ```

=== "Output"

    ```bash
    > python get_last_stk.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0            61514177                  2                       7        134.37                      0                  3                       7        134.42                      0    2022-12-16
    ```


## Real-time option snapshots

Let's try a low-latency snapshot request for the most recent option quote available:

=== "get_last_opt.py"

    ```python
    --8<-- "docs/get_last_opt.py"
    ```

=== "Output"

    ```bash
    > python get_last_opt.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0            57599990                  1                       1          6.05                     50                 63                      46          6.55                     50    2022-12-16
    ```