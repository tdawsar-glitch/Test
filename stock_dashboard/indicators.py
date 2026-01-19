"""Technical indicator calculations."""

import pandas as pd


def add_sma(data: pd.DataFrame, windows: list[int]) -> pd.DataFrame:
    result = data.copy()
    for window in windows:
        result[f"SMA {window}"] = result["Close"].rolling(window=window, min_periods=1).mean()
    return result


def add_macd(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    exp12 = result["Close"].ewm(span=12, adjust=False).mean()
    exp26 = result["Close"].ewm(span=26, adjust=False).mean()
    result["MACD"] = exp12 - exp26
    result["Signal"] = result["MACD"].ewm(span=9, adjust=False).mean()
    result["Histogram"] = result["MACD"] - result["Signal"]
    return result


def add_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    result = data.copy()
    delta = result["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    result["RSI"] = 100 - (100 / (1 + rs))
    return result


def build_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add supported technical indicators to the dataset."""
    result = add_sma(data, [20, 50, 200])
    result = add_macd(result)
    result = add_rsi(result)
    return result
