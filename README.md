# decorator-utils

Python package providing utilities for writing decorators and decorator factories. It also provides a number of useful
decorators, such as argument type-checking, schema validation, type conversion etc.

## Installation

This package is made easily available via pip:

```bash
pip install decorator-utils
```

## Quickstart

Here is an example using one of the convenience decorators to check the input dataframe columns:

```python
import pandas as pd
from decorator_utils.misc import required_columns

@required_columns(["id", "name", "value"])
def some_function(df: pd.DataFrame) -> pd.DataFrame:
    return df[["id", "name", "value"]].describe()
```
