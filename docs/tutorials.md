In this section you'll learn how to get started with the code in this project.

# Quickstart

## Installation

- Install Python 3.
- Using pip, Python's package manager, open a terminal and run
`pip install thetadata`
or
`python -m pip install thetadata`

## READ THIS!

You will not be able to use Theta Data unless you instaniate a ThetaClient object with the `username` and `passwd` fields. These examples do not instaniate ThetaClient that way but you should. An example of proper ThetaClient instantiation is:

```client = ThetaClient(username="my_theta_data_email", passwd="my_thetadata_passwd")```

## Free data

### Get end of day data

With the API installed, you can now
`import thetadata` in any Python script you'd like!

Here's how you may make your first (**free**) request:

=== "end_of_day.py"

    ```python
    --8<-- "docs/end_of_day.py"
    ```

=== "Output"

    ```bash
    > python end_of_day.py                                                                                                                                                                         1 ✘ 
       DataType.OPEN  DataType.HIGH  DataType.LOW  DataType.CLOSE  DataType.VOLUME  DataType.COUNT DataType.DATE
    0          13.25          13.25         10.15           10.20              214              21    2022-07-18
    1          10.90          12.95         10.09           12.93               62              20    2022-07-19
    2          14.05          15.04         14.05           15.04               16               7    2022-07-20
    3          14.45          16.64         14.05           16.36              142              44    2022-07-21
    4          17.06          17.06         15.00           15.32               49               9    2022-07-22
    ```

    > *What am I looking at?*

### Understanding the output

The return type of `end_of_day` is a `DataFrame`, a core datatype in the **pandas** package.

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
    close_price=10.2
    ```

    As you can see, the response contains 7 fields (DataFrame *columns*), and
    the close price of the first *row* of this data (which represents July 18, 2022) is $13.10.

Congratulations, you've made and processed your first request!

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

## Get last option

Now let's try a low-latency request for the most recent option data available:

Note that *as of now*, live data requests will only work during trading hours!

=== "get_last.py"

    ```python
    --8<-- "docs/get_last.py"
    ```

=== "Output"

    ```bash
    > python get_last.py
       DataType.MS_OF_DAY  DataType.BID_SIZE  DataType.BID_CONDITION  DataType.BID  DataType.BID_EXCHANGE  DataType.ASK_SIZE  DataType.ASK_CONDITION  DataType.ASK  DataType.ASK_EXCHANGE DataType.DATE
    0            57599874                 52                       7         20.05                     50                 68                       7         20.35                     50    2022-08-02
    ```

## What's next?

Nice! You are now familiar the `Series` and `DataFrame` objects, the return types of our data requests.
Using the skills learned in these tutorials, you're well on your way to mastering the entire `thetadata` package.
Explore other requests at your disposal on the API Reference page!

For more details on the `pandas` API, please see the [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html).
