import datetime as dt

import pandas as pd
import streamlit as st

from stock_dashboard import config
from stock_dashboard.data_loader import load_price_data
from stock_dashboard.indicators import build_indicators, generate_trading_signals

st.set_page_config(page_title="Stock Indicator Dashboard", layout="wide")

st.title("Stock Indicator Dashboard")
st.caption("Powered by yfinance")

st.sidebar.header("Controls")
selected_ticker = st.sidebar.selectbox(
    "Ticker",
    config.SUPPORTED_TICKERS,
    index=config.SUPPORTED_TICKERS.index(config.DEFAULT_TICKER),
)
end_date = st.sidebar.date_input("End date", dt.date.today())
start_date = st.sidebar.date_input(
    "Start date",
    end_date - dt.timedelta(days=config.DEFAULT_LOOKBACK_DAYS),
    max_value=end_date,
)
interval = st.sidebar.selectbox(
    "Interval",
    config.INTERVAL_OPTIONS,
    index=0,
)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_ticker_data(ticker: str, start: dt.date, end: dt.date, interval_value: str) -> pd.DataFrame:
    return load_price_data(ticker, start, end, interval_value)


with st.spinner(f"Loading {selected_ticker} data..."):
    data = load_ticker_data(selected_ticker, start_date, end_date, interval)

if data.empty:
    st.warning("No data returned for the selected date range.")
    st.stop()

latest_close = float(data["Close"].iloc[-1])
latest_open = float(data["Open"].iloc[-1])
latest_volume = int(data["Volume"].iloc[-1])

col1, col2, col3 = st.columns(3)
col1.metric("Latest Close", f"${latest_close:,.2f}")
col2.metric("Latest Open", f"${latest_open:,.2f}")
col3.metric("Latest Volume", f"{latest_volume:,}")

st.subheader("Price History")
indicator_data = build_indicators(data)
price_columns = ["Open", "Close", "SMA 20", "SMA 50", "SMA 200"]
st.line_chart(indicator_data[price_columns])

st.subheader("Trading Signals")
signals = generate_trading_signals(indicator_data)
for signal in signals:
    st.markdown(f"**{signal['title']}**: {signal['summary']}")

st.subheader("MACD")
st.line_chart(indicator_data[["MACD", "Signal"]])
st.bar_chart(indicator_data["Histogram"])

st.subheader("RSI")
st.line_chart(indicator_data["RSI"])

st.subheader("Raw Data")
st.dataframe(indicator_data, use_container_width=True)
