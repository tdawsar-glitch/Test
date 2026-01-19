import datetime as dt

import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="SPY Stock Dashboard", layout="wide")

st.title("SPY Stock Dashboard")
st.caption("Powered by yfinance")

st.sidebar.header("Controls")
end_date = st.sidebar.date_input("End date", dt.date.today())
start_date = st.sidebar.date_input(
    "Start date",
    end_date - dt.timedelta(days=365),
    max_value=end_date,
)
interval = st.sidebar.selectbox(
    "Interval",
    ["1d", "1wk", "1mo"],
    index=0,
)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_spy_data(start: dt.date, end: dt.date, interval_value: str):
    return yf.download("SPY", start=start, end=end + dt.timedelta(days=1), interval=interval_value)


with st.spinner("Loading SPY data..."):
    data = load_spy_data(start_date, end_date, interval)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

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
data["SMA 20"] = data["Close"].rolling(window=20).mean()
data["SMA 50"] = data["Close"].rolling(window=50).mean()
data["SMA 200"] = data["Close"].rolling(window=200).mean()
st.line_chart(data[["Open", "Close", "SMA 20", "SMA 50", "SMA 200"]])

st.subheader("MACD")
exp12 = data["Close"].ewm(span=12, adjust=False).mean()
exp26 = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"] = exp12 - exp26
data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
data["Histogram"] = data["MACD"] - data["Signal"]
st.line_chart(data[["MACD", "Signal"]])
st.bar_chart(data["Histogram"])

st.subheader("Raw Data")
st.dataframe(data, use_container_width=True)
