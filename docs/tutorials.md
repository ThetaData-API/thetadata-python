In this section you'll learn how to get started with the code in this project.

# Quickstart
In order to use this API you must run the **Theta Terminal** alongside your application. Please see the [Theta Terminal setup guide](https://www.thetadata.net/terminal-setup) for more information.

## Installation

- Install Python 3.
- Using pip, Python's package manager, open a terminal and run
`pip install thetadata`

## Get last (our first request)

With the **Theta Terminal** connected and the API installed, you're now free
to `import thetadata` in any Python script you'd like!

Here's how you might make a request:

=== "first_request.py"

    ```python
    --8<-- "docs/first_request.py"
    ```

=== "Output"

    ```bash
    > python first_request.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  ...  DataType.ASK_EXCHANGE  DataType.DATE
    0            57599954                 84  ...                     50     2022-07-26

    [1 rows x 10 columns]
    ```

    > *What am I looking at?*

### Understanding the output

The return type of `get_last_option` is a `DataFrame`, a core datatype in the **pandas** package.

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
    Index([    DataType.MS_OF_DAY,      DataType.BID_SIZE, DataType.BID_CONDITION,
                     DataType.BID,  DataType.BID_EXCHANGE,      DataType.ASK_SIZE,
           DataType.ASK_CONDITION,           DataType.ASK,  DataType.ASK_EXCHANGE,
                    DataType.DATE],
          dtype='object')
    bid_price=13.1
    ```

    As you can see, the response contains 10 fields (DataFrame *columns*), and
    the bid price of this request is $13.10.

Congratulations, you've made your first request!

## List roots

Let's try another common request, listing all root symbols for options. 

=== "list_roots.py"

    ```python
    --8<-- "docs/list_roots.py"
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

Unlike the previous
request, `get_roots` returns a *Series*. In the pandas package, a
`Series` is a one-dimensional array, similar to a Python list.


### Manipulating a `Series`

The above example returned a `Series`. Let's see how we can use it to process our data.

=== "manipulate_series.py"

    ```python
    --8<-- "docs/manipulate_series.py"
    ```

=== "Output"

    ```bash
    > python manipulate_series.py
    contains_apple=True
    count=6246
    len(filtered)=530
    ```

Nice! You are now familiar the `Series` and `DataFrame` objects, the return types of our data requests!

For more details on the pandas API, please see the [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html).
