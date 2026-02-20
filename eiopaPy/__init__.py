"""
eiopapy -- Python client for EIOPA risk-free rate data.

This is a Python port of the R package eiopaR by Mehdi Echchelh:
https://github.com/MehdiChelh/eiopaR

The data is accessed through the same REST API used by the R package.
Neither this package nor its author are affiliated with EIOPA.
"""

from eiopapy.client import (
    EiopaRFR,
    get_options,
    get_rfr,
    get_rfr_no_va,
    get_rfr_with_va,
)

__version__ = "0.1.0"

__all__ = [
    "EiopaRFR",
    "get_options",
    "get_rfr",
    "get_rfr_no_va",
    "get_rfr_with_va",
]
