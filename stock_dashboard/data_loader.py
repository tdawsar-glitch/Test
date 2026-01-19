"""Data loading helpers for the dashboard."""

import datetime as dt

import pandas as pd
import yfinance as yf


@pd.api.extensions.register_dataframe_accessor("price")
class PriceAccessor:
    """Convenience accessors for price data."""

    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def normalize_columns(self) -> pd.DataFrame:
        data = self._obj
        if isinstance(data.columns, pd.MultiIndex):
            data = data.copy()
            data.columns = data.columns.get_level_values(0)
        return data


@pd.api.extensions.register_dataframe_accessor("market")
class MarketAccessor:
    """Extra data cleanup helpers."""

    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def ensure_types(self) -> pd.DataFrame:
        data = self._obj.copy()
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")
        return data


def load_price_data(ticker: str, start: dt.date, end: dt.date, interval_value: str) -> pd.DataFrame:
    """Download price data for a ticker."""
    data = yf.download(
        ticker,
        start=start,
        end=end + dt.timedelta(days=1),
        interval=interval_value,
        progress=False,
    )
    return data.price.normalize_columns().market.ensure_types()
