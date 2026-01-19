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


def generate_trading_signals(indicator_data: pd.DataFrame) -> list[dict]:
    """Create two trading signals based on RSI and MACD."""
    latest = indicator_data.iloc[-1]
    previous = indicator_data.iloc[-2] if len(indicator_data) > 1 else latest

    signals = []

    rsi_value = latest.get("RSI")
    if pd.isna(rsi_value):
        rsi_summary = "RSI data is not available yet."
    elif rsi_value >= 70:
        rsi_summary = f"RSI is {rsi_value:.1f}, indicating overbought momentum."
    elif rsi_value <= 30:
        rsi_summary = f"RSI is {rsi_value:.1f}, indicating oversold momentum."
    else:
        rsi_summary = f"RSI is {rsi_value:.1f}, indicating neutral momentum."
    signals.append(
        {
            "title": "RSI Momentum",
            "summary": rsi_summary,
        }
    )

    macd_value = latest.get("MACD")
    signal_value = latest.get("Signal")
    prev_macd = previous.get("MACD")
    prev_signal = previous.get("Signal")

    if pd.isna(macd_value) or pd.isna(signal_value):
        macd_summary = "MACD data is not available yet."
    elif macd_value > signal_value and prev_macd <= prev_signal:
        macd_summary = "MACD just crossed above the signal line, a bullish momentum shift."
    elif macd_value < signal_value and prev_macd >= prev_signal:
        macd_summary = "MACD just crossed below the signal line, a bearish momentum shift."
    elif macd_value > signal_value:
        macd_summary = "MACD is above the signal line, indicating bullish momentum."
    else:
        macd_summary = "MACD is below the signal line, indicating bearish momentum."

    signals.append(
        {
            "title": "MACD Trend",
            "summary": macd_summary,
        }
    )

    return signals
