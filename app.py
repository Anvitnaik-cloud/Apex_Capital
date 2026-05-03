import os
import streamlit as st
import pandas as pd

from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.news_panel import render_news_panel
from components.sip import render_sip_calculator
from components.metrics import render_trend_metrics
from models.forecasting import run_model_suite
from utils.data import get_ticker_data, get_ticker_info
from utils.indicators import add_indicators


st.set_page_config(
    page_title="Apex Capital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("Apex Capital")

nav, asset_type, period, horizon, run_models = render_sidebar()

if nav == "Assets":
    st.subheader("Asset Selection")
    ticker_input = st.text_input("Enter a ticker symbol", value="AAPL").upper().strip()
    ticker_file = st.file_uploader("Or upload a file with a ticker symbol", type=["txt", "csv"])

    ticker = ticker_input
    if ticker_file is not None:
        try:
            content = ticker_file.getvalue().decode("utf-8", errors="ignore").strip()
            if ticker_file.name.lower().endswith(".csv"):
                df = pd.read_csv(ticker_file)
                if "ticker" in df.columns:
                    ticker = str(df["ticker"].iloc[0]).upper().strip()
                else:
                    ticker = str(df.iloc[0, 0]).upper().strip()
            else:
                ticker = content.split()[0].upper().strip()
        except Exception:
            st.warning("Unable to read ticker from the uploaded file. Using the text input instead.")

    if not ticker:
        st.info("Enter a valid ticker symbol to begin.")
        st.stop()

    with st.spinner("Fetching market data..."):
        data = get_ticker_data(ticker, period=period)

    if data is None or data.empty:
        st.error("No data found for that ticker. Check the symbol, internet access, or try a shorter period.")
        st.stop()

    data = add_indicators(data)
    info = get_ticker_info(ticker)

    tab_trend, tab_news, tab_dash = st.tabs(
        ["Trend & Prediction", "News", "Dashboard"]
    )

    with tab_trend:
        render_trend_metrics(data, ticker)

        if run_models:
            with st.spinner("Training models and generating predictions..."):
                model_results = run_model_suite(data, horizon=horizon)

            if model_results["errors"]:
                for err in model_results["errors"]:
                    st.warning(err)

            if model_results["predictions"]:
                st.subheader("Predicted Prices")
                pred_df = pd.DataFrame(model_results["predictions"])
                st.dataframe(pred_df, use_container_width=True)

            if model_results["metrics"]:
                st.subheader("Model Performance")
                metrics_df = pd.DataFrame(model_results["metrics"]).set_index("model")
                st.dataframe(metrics_df, use_container_width=True)

        st.download_button(
            label="Download Historical Data (CSV)",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name=f"{ticker}_historical.csv",
            mime="text/csv",
        )

    with tab_news:
        render_news_panel(ticker, asset_type)

    with tab_dash:
        if st.button("Open Dashboard Analysis"):
            render_dashboard(data, info, ticker)

elif nav == "Mutual Funds":
    render_sip_calculator()

st.caption("Apex Capital | Financial analytics platform")
