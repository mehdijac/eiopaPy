"""
Basic tests for eiopapy.

These tests call the live API, so they require an internet connection.
Run with: pytest tests/
"""

import pandas as pd
import pytest

from eiopapy import EiopaRFR, get_options, get_rfr, get_rfr_no_va, get_rfr_with_va


class TestGetOptions:
    def test_returns_list(self):
        result = get_options("region")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_region_contains_FR(self):
        regions = get_options("region")
        assert "FR" in regions


class TestGetRfr:
    def test_with_va_single_year(self):
        rfr = get_rfr_with_va("FR", year=2019, month=12)
        assert isinstance(rfr, EiopaRFR)
        assert isinstance(rfr.data, pd.DataFrame)
        assert not rfr.data.empty
        assert not rfr.metadata.empty

    def test_no_va_single_year(self):
        rfr = get_rfr_no_va("FR", year=2019, month=12)
        assert isinstance(rfr, EiopaRFR)
        assert not rfr.data.empty

    def test_multiple_years(self):
        rfr = get_rfr("with_va", "FR", year=[2017, 2018], month=12)
        # Should have 2 columns (one per year)
        assert rfr.data.shape[1] == 2
        assert rfr.metadata.shape[0] == 2

    def test_repr(self):
        rfr = get_rfr_with_va("FR", year=2019, month=12)
        text = repr(rfr)
        assert "<EiopaRFR>" in text

    def test_invalid_region_type(self):
        with pytest.raises(ValueError):
            get_rfr("with_va", "", year=2019, month=12)
