# Deductable

de-duck-table
A way to deduce new columns in your duckdb table 

## Description

For a client I was doing research on a collection of websites.  I wanted an easy way to add a column with findings based
on the previous information.  For instance, I started with a list of names, for which i didn't have the URL. 
An agent took in the name, and found the website url. 

## Installation

```bash
uv pip install deductable
```

## Requirements

- Python 3.13+
- DuckDB 1.4.1+
- Loguru 0.7.3+
- Pandas 2.3.3+

## Quick Start

```python
from typing import Optional
import duckdb
from deductable import Deductable
from my_agents import find_url

# Connect to a DuckDB database
with duckdb.connect('companies.duckdb') as con:
    # Create a Deductable instance for the table
    # Deductable expects at least an id column
    dt = Deductable(con, table_name="companies")

    @dt.column
    def company_url(company_name: str) -> Optional[float]:
        # company_name should be a column in the duckdb
        return find_url(company_name)

    # Apply the column function to populate the weight column
    dt.materialize()

    # View the result
    print(dt.df())
```

## Features

- **Type-safe column functions**: Define column functions with proper type annotations
- **Automatic column creation**: Columns are automatically created based on function names
- **Dependency handling**: Functions can depend on other columns
- **Optional values**: Support for nullable columns with Optional type annotations
- **Pandas integration**: Easy conversion to pandas DataFrames


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
