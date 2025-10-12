import pytest
import pandas as pd
from odd_kernel.datasets.finance.marketdata import MarketDataProvider, DataField, Period, TimeUnit


@pytest.fixture(scope="module")
def market_data_provider():
    """Create a MarketData instance to reuse across tests."""
    return MarketDataProvider()


@pytest.fixture(scope="module")
def ticker():
    """Use a stable ticker with long history."""
    return "AAPL"


@pytest.fixture(scope="module")
def date_range():
    """Provide a small date range for tests"""
    return ("2020-12-31", "2025-12-31")


# ------------------------------------------------------------
# ENUMS AND BASIC CLASSES
# ------------------------------------------------------------

def test_period_to_pandas_freq():
    p = Period(3, TimeUnit.DAYS)
    assert p.to_pandas_freq() == "3D"

    p2 = Period(1, TimeUnit.MONTHS)
    assert str(p2) == "1M"


def test_period_invalid_value():
    with pytest.raises(ValueError):
        Period(0, TimeUnit.DAYS)


# ------------------------------------------------------------
# DOWNLOAD AND SUMMARY
# ------------------------------------------------------------

def test_download_and_cache(market_data_provider, ticker, date_range):
    start, end = date_range
    df1 = market_data_provider._download(ticker, start, end)
    df2 = market_data_provider._download(ticker, start, end)
    # Cached object should be the same
    assert df1 is df2
    assert not df1.empty
    assert "Close" in df1.columns


def test_get_available_fields(market_data_provider, ticker, date_range):
    start, end = date_range
    fields = market_data_provider.get_available_fields(ticker, start, end)
    print(fields)
    assert isinstance(fields, list)
    assert DataField.CLOSE in fields


def test_get_summary(market_data_provider, ticker, date_range):
    start, end = date_range
    summary = market_data_provider.get_summary([ticker], start, end)
    assert isinstance(summary, pd.DataFrame)
    assert "fields" in summary.columns
    assert ticker in summary["name"].values


# ------------------------------------------------------------
# RAW AND INTERPOLATED DATA
# ------------------------------------------------------------

def test_get_raw_close_field(market_data_provider, ticker, date_range):
    start, end = date_range
    df = market_data_provider.get_raw(ticker, start, end, DataField.CLOSE)
    assert isinstance(df, pd.DataFrame)
    assert "value" in df.columns
    assert df.index.is_monotonic_increasing


def test_get_raw_invalid_field(market_data_provider, ticker, date_range):
    start, end = date_range
    with pytest.raises(ValueError):
        market_data_provider.get_raw(ticker, start, end, DataField("Nonexistent"))


def test_get_interpolated_daily(market_data_provider, ticker, date_range):
    start, end = date_range
    p = Period(1, TimeUnit.DAYS)
    interp = market_data_provider.get_interpolated(ticker, start, end, DataField.CLOSE, p)

    assert isinstance(interp, pd.DataFrame)
    assert "value" in interp.columns
    assert interp.index.freq is not None or len(interp) > 0
    # Should cover entire date range
    assert interp.index.min() >= pd.Timestamp(start)
    assert interp.index.max() <= pd.Timestamp(end)


def test_interpolation_fills_missing_values(market_data_provider, ticker, date_range):
    """Ensure interpolation fills gaps correctly."""
    start, end = date_range
    p = Period(1, TimeUnit.DAYS)
    interp = market_data_provider.get_interpolated(ticker, start, end, DataField.CLOSE, p)
    assert interp["value"].isna().sum() == 0
