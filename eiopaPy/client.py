"""
Core API client for accessing EIOPA risk-free rate data.

This module handles all HTTP communication with the API hosted at
https://mehdiechchelh.com/api/. It provides low-level functions
(api_get, build paths) and high-level functions (get_rfr, etc.)
that return parsed pandas DataFrames.
"""

from typing import List, Optional, Union

import requests
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE_URL = "https://mehdiechchelh.com/api"

# The two curve types supported by the API
WITH_VA = "with_va"
NO_VA = "no_va"


# ---------------------------------------------------------------------------
# Path builders -- they construct the URL path for each endpoint
# ---------------------------------------------------------------------------

def _path_get_options(field: str) -> str:
    """Build the URL path to query available options for a given field.

    For example, _path_get_options("region") returns the path that lists
    all available region codes (FR, BE, DE, ...).
    """
    return f"{API_BASE_URL}/{field}"


def _path_get_rfr(
    rfr_type: str,
    region: str,
    year: str = "",
    month: str = "",
) -> str:
    """Build the URL path to query risk-free rates.

    Parameters
    ----------
    rfr_type : str
        "with_va" or "no_va".
    region : str
        Country/region code (e.g. "FR").
    year : str
        Comma-separated years (e.g. "2017,2018") or empty string.
    month : str
        Comma-separated months (e.g. "12") or empty string.
    """
    path = f"{API_BASE_URL}/{rfr_type}/{region}"
    params = []
    if year:
        params.append(f"year={year}")
    if month:
        params.append(f"month={month}")
    if params:
        path += "?" + "&".join(params)
    return path


# ---------------------------------------------------------------------------
# Low-level HTTP helper
# ---------------------------------------------------------------------------

def _api_get(url: str) -> dict:
    """Send a GET request to the API and return the parsed JSON response.

    Raises
    ------
    requests.HTTPError
        If the API returns a non-2xx status code.
    ConnectionError
        If the API is unreachable.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

class EiopaRFR:
    """Container for EIOPA risk-free rate data.

    Attributes
    ----------
    data : pd.DataFrame
        A DataFrame where each column is a risk-free rate curve
        (identified by something like "20171231_rfr_spot_with_va_FR")
        and each row is a maturity (row 0 = 1 year, row 1 = 2 years, ...).
    metadata : pd.DataFrame
        A DataFrame with one row per curve, containing all the metadata
        fields returned by the API (id, type, region, year, month, ...).
    """

    def __init__(self, data: pd.DataFrame, metadata: pd.DataFrame):
        self.data = data
        self.metadata = metadata

    def __repr__(self) -> str:
        lines = ["<EiopaRFR>"]
        for _, row in self.metadata.iterrows():
            curve_id = row.get("id", "?")
            values = self.data[curve_id].head(3).tolist()
            preview = ", ".join(str(v) for v in values)
            lines.append(f"  {curve_id} > {preview} ...")
        return "\n".join(lines)


def _parse_rfr(raw_json: list) -> EiopaRFR:
    """Parse the raw JSON array returned by the API into an EiopaRFR object.

    Each element of raw_json is a dict with metadata fields (id, type, ...)
    plus a "data" key containing the list of rate values.
    """
    if not raw_json:
        return EiopaRFR(data=pd.DataFrame(), metadata=pd.DataFrame())

    # -- Extract metadata (everything except "data") -----------------------
    metadata_rows = []
    for item in raw_json:
        meta = {k: v for k, v in item.items() if k != "data"}
        metadata_rows.append(meta)
    metadata = pd.DataFrame(metadata_rows)

    # -- Extract rate curves -----------------------------------------------
    data_dict = {}
    for item in raw_json:
        curve_id = item.get("id", "unknown")
        data_dict[curve_id] = item["data"]
    data = pd.DataFrame(data_dict)

    return EiopaRFR(data=data, metadata=metadata)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_options(field: str) -> list:
    """Return available values for a given field.

    Parameters
    ----------
    field : str
        One of "region", "year", or "month".

    Returns
    -------
    list
        The list of available values (e.g. ["AT", "BE", "FR", ...]).

    Examples
    --------
    >>> from eiopapy import get_options
    >>> regions = get_options("region")
    >>> print(regions)
    """
    url = _path_get_options(field)
    return _api_get(url)


def get_rfr(
    rfr_type: str,
    region: str,
    year: Optional[Union[int, List[int]]] = None,
    month: Optional[Union[int, List[int]]] = None,
) -> EiopaRFR:
    """Query EIOPA risk-free rate curves.

    This is the main function. It calls the API, parses the response,
    and returns an EiopaRFR object whose .data attribute is a DataFrame.

    Parameters
    ----------
    rfr_type : str
        Type of curve: "with_va" (with volatility adjustment) or "no_va"
        (without volatility adjustment).
    region : str
        Country/region code, e.g. "FR", "BE", "DE".
    year : int or list of int, optional
        Year(s) to query. If None, all available years are returned.
    month : int or list of int, optional
        Month(s) to query. If None, all available months are returned.

    Returns
    -------
    EiopaRFR
        An object with .data (DataFrame of rate curves) and .metadata.

    Examples
    --------
    >>> from eiopapy import get_rfr
    >>> rfr = get_rfr("with_va", "FR", year=[2017, 2018], month=12)
    >>> print(rfr.data.head())
    """
    # Validate inputs
    if not isinstance(region, str) or len(region) == 0:
        raise ValueError("'region' must be a non-empty string.")

    # Convert year/month to comma-separated strings for the API
    year_str = ""
    if year is not None:
        if isinstance(year, (list, tuple)):
            year_str = ",".join(str(y) for y in year)
        else:
            year_str = str(year)

    month_str = ""
    if month is not None:
        if isinstance(month, (list, tuple)):
            month_str = ",".join(str(m) for m in month)
        else:
            month_str = str(month)

    url = _path_get_rfr(rfr_type, region, year_str, month_str)
    raw = _api_get(url)

    return _parse_rfr(raw)


def get_rfr_with_va(
    region: str,
    year: Optional[Union[int, List[int]]] = None,
    month: Optional[Union[int, List[int]]] = None,
) -> EiopaRFR:
    """Query EIOPA risk-free rates WITH volatility adjustment.

    This is a convenience wrapper around get_rfr with rfr_type="with_va".

    Parameters
    ----------
    region : str
        Country/region code, e.g. "FR".
    year : int or list of int, optional
        Year(s) to query.
    month : int or list of int, optional
        Month(s) to query.

    Returns
    -------
    EiopaRFR

    Examples
    --------
    >>> from eiopapy import get_rfr_with_va
    >>> rfr = get_rfr_with_va("FR", year=[2017, 2018], month=12)
    >>> print(rfr.data.head())
    """
    return get_rfr(WITH_VA, region, year=year, month=month)


def get_rfr_no_va(
    region: str,
    year: Optional[Union[int, List[int]]] = None,
    month: Optional[Union[int, List[int]]] = None,
) -> EiopaRFR:
    """Query EIOPA risk-free rates WITHOUT volatility adjustment.

    This is a convenience wrapper around get_rfr with rfr_type="no_va".

    Parameters
    ----------
    region : str
        Country/region code, e.g. "FR".
    year : int or list of int, optional
        Year(s) to query.
    month : int or list of int, optional
        Month(s) to query.

    Returns
    -------
    EiopaRFR

    Examples
    --------
    >>> from eiopapy import get_rfr_no_va
    >>> rfr = get_rfr_no_va("FR", year=2019, month=12)
    >>> print(rfr.data.head())
    """
    return get_rfr(NO_VA, region, year=year, month=month)
