In this section you'll learn how to get started with the code in this project.

> **Note:** Finding a concept confusing? Let us know!


# Quickstart
In order to use this API you must run the **Theta Terminal** alongside your application. Please see the [Theta Terminal setup guide](https://www.thetadata.net/terminal-setup) for more information.

## Installation

- Install Python 3.
- Using pip, Python's package manager, open a terminal and run
`pip install thetadata`

## Make your first request

With the **Theta Terminal** connected and the API installed, you're now free
to `import thetadata` in any Python script you'd like!

Here's how you might make a request:

```python
import pandas as pd
from thetadata import ThetaClient, SecType

# Create a ThetaClient
client = ThetaClient()

# Connect to the Terminal
with client.connect():

    # List all root symbols for options
    roots: pd.Series = client.get_roots(sec=SecType.OPTION)

print(roots)
```

### Understanding the output

Running this script will produce the following:

```bash
> python script.py
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
> *What am I looking at?*

The return type of `get_roots` is a `Series`, a core datatype in the **pandas** package.

> [pandas](https://pandas.pydata.org/) is a fast, powerful, flexible and easy to use open source data
> analysis and manipulation tool, built on top of the Python programming language.

Furthermore, pandas is extremely popular. According to [learnpython.com](https://learnpython.com/blog/most-popular-python-packages/), pandas is the second most popular Python package, losing only to numpy, which is used extensively by pandas.

### Manipulating the output

The [official pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html)
covers significantly more material than this tutorial. However, a key takeaway is that
pandas operates on two data structures:

1. `Series`
2. `DataFrame`

A *Series* is a one-dimensional array, similar to a Python list. A *DataFrame* is a two-dimensional data structure with rows and columns, similar to a spreadsheet.

The above example returned a `Series`. Let's see how we can use it to process our data.

```python
# -- SNIPPET --
    roots: pd.Series = client.get_roots(sec=SecType.OPTION)

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
```
```bash
> python script.py
contains_apple=True
count=6246
len(filtered)=530
```

Congratulations, you've completed your first request!
