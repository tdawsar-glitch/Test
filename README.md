# SPY Streamlit App

This Streamlit app pulls SPY stock data from `yfinance` and visualizes price history along with basic metrics.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Windows Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you are using Command Prompt instead of PowerShell, activate with:

```bat
.venv\Scripts\activate.bat
```

## Run

```bash
streamlit run app.py
```

## Run on Windows

```powershell
streamlit run app.py
```
