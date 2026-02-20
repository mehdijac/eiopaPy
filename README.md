# eiopapy

Python client for accessing EIOPA risk-free rate (RFR) term structures.

This project is a **Python port** of the R package
[eiopaR](https://github.com/MehdiChelh/eiopaR) created by
[Mehdi Echchelh](https://github.com/MehdiChelh). It uses the same REST API
(`https://mehdiechchelh.com/api/`) to retrieve the data.

**Important notes:**

- This package requires an internet connection.
- Neither this package nor its author are affiliated with EIOPA.
- Please limit the number of API calls. Your IP can be temporarily or
  permanently blocked if too many queries are executed. Store the results
  in variables rather than calling the functions repeatedly.

For more information on the data itself, see
[EIOPA Risk-free interest rate term structures](https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en).


## Installation

```bash
pip install .
```

Or in development mode:

```bash
pip install -e ".[dev]"
```

Dependencies: `requests` and `pandas`.


## Usage

### Get risk-free rates with volatility adjustment

```python
from eiopapy import get_rfr_with_va

rfr = get_rfr_with_va("FR", year=[2017, 2018], month=12)
print(rfr)
# <EiopaRFR>
#   20171231_rfr_spot_with_va_FR > -0.00318, -0.0021, -0.00048 ...
#   20181231_rfr_spot_with_va_FR > -0.00093, -0.00035, 0.00063 ...
```

### Access the data as a pandas DataFrame

```python
print(rfr.data.head())
#    20171231_rfr_spot_with_va_FR  20181231_rfr_spot_with_va_FR
# 0                      -0.00318                      -0.00093
# 1                      -0.00210                      -0.00035
# 2                      -0.00048                       0.00063
# 3                       0.00109                       0.00194
# 4                       0.00249                       0.00339
```

### Get risk-free rates without volatility adjustment

```python
from eiopapy import get_rfr_no_va

rfr = get_rfr_no_va("FR", year=2019, month=12)
print(rfr.data.head())
```

### Use the generic function with explicit type

```python
from eiopapy import get_rfr

rfr = get_rfr("with_va", "BE", year=2020, month=11)
```

### List available options

```python
from eiopapy import get_options

regions = get_options("region")
years = get_options("year")
months = get_options("month")
```

### Plot a curve

```python
import matplotlib.pyplot as plt

rfr = get_rfr_with_va("FR", year=2017, month=12)
col = rfr.data.columns[0]
rfr.data[col].plot(title=col)
plt.xlabel("Maturity (years)")
plt.ylabel("Rate")
plt.show()
```


## API reference

| Function | Description |
|---|---|
| `get_rfr(rfr_type, region, year, month)` | Generic query. `rfr_type` is `"with_va"` or `"no_va"`. |
| `get_rfr_with_va(region, year, month)` | Shortcut for rates with volatility adjustment. |
| `get_rfr_no_va(region, year, month)` | Shortcut for rates without volatility adjustment. |
| `get_options(field)` | List available values for `"region"`, `"year"`, or `"month"`. |

All `get_rfr*` functions return an `EiopaRFR` object with two attributes:

- `data` -- a `pandas.DataFrame` with one column per curve and one row per maturity.
- `metadata` -- a `pandas.DataFrame` with one row per curve and the associated metadata fields.


## Comparison with the R version

| R (eiopaR) | Python (eiopapy) |
|---|---|
| `get_rfr("with_va", "FR", 2019, 12)` | `get_rfr("with_va", "FR", year=2019, month=12)` |
| `get_rfr_with_va("FR", 2017:2018, 12)` | `get_rfr_with_va("FR", year=[2017, 2018], month=12)` |
| `rfr$data` | `rfr.data` |
| `get_options("region")` | `get_options("region")` |


## Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

Note: tests call the live API and require an internet connection.


## Credit

- Original R package: [eiopaR](https://github.com/MehdiChelh/eiopaR) by Mehdi Echchelh.
- Data source: [EIOPA](https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en).


## License

MIT
