# Apex Capital

A professional Streamlit-based financial analytics and stock prediction dashboard.

## Features
- Multi-model stock forecasting (KNN, Linear Regression, ARIMA, LSTM)
- Trend analysis with moving averages and volume
- News aggregation with optional sentiment scoring
- Interactive dashboard with Plotly visualizations
- SIP calculator for mutual fund planning

## Setup

1. Create a virtual environment (optional but recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set optional NewsAPI key:

```bash
setx NEWSAPI_KEY "your_key_here"
```

4. Run the app:

```bash
streamlit run app.py
```

## Notes
- LSTM requires TensorFlow; if it fails to import, the app will skip LSTM predictions.
- Data is fetched from Yahoo Finance via `yfinance`.
- News uses NewsAPI if configured, otherwise Google News RSS.
