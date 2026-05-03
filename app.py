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
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Monoton&display=swap');

    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0F0F0F; color: #F5F5F5; }
    h1, h2, h3 { font-weight: 500; letter-spacing: -0.5px; color: #F5F5F5; }
    p, span, label { color: #888; font-weight: 300; }

    section[data-testid="stSidebar"] { background-color: #0F0F0F; border-right: 1px solid #1E1E1E; }
    .sidebar-title { font-size: 22px; font-weight: 500; color: #F5F5F5; margin-bottom: 12px; }
    .brand-title { font-family: 'Monoton', sans-serif; font-weight: 400; font-style: normal; letter-spacing: 1px; }
    .sidebar-section { font-size: 12px; letter-spacing: 0.6px; text-transform: uppercase; color: #888; margin: 12px 0 6px; }

    section[data-testid="stSidebar"] .stRadio label { border-left: 2px solid transparent; padding-left: 10px; }
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) { border-left-color: #7B61FF; color: #F5F5F5; }

    .stTextInput input, .stSelectbox select, .stNumberInput input { background: #161616; border: 1px solid #1E1E1E; color: #F5F5F5; }

    .stButton button, .stDownloadButton button { background: transparent; border: 1px solid #F5F5F5; color: #F5F5F5; border-radius: 6px; }
    .stButton button:hover, .stDownloadButton button:hover { border-color: #7B61FF; color: #F5F5F5; }

    div[data-testid="stMetric"] { background: transparent; border: none; padding: 16px 0; }
    div[data-testid="stMetricLabel"] { font-size: 12px; color: #888; font-weight: 300; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 500; color: #F5F5F5; }
    div[data-testid="stMetricDelta"] { font-size: 12px; color: #7B61FF; }

    .price-header { display: flex; align-items: baseline; gap: 12px; margin: 8px 0 20px; }
    .price-header .ticker { font-size: 36px; font-weight: 500; color: #F5F5F5; }
    .price-header .price { font-size: 36px; font-weight: 500; color: #F5F5F5; }
    .price-header .badge { font-size: 12px; color: #7B61FF; border: 1px solid #1E1E1E; padding: 2px 8px; border-radius: 6px; }

    .news-card { background: #1A1A1A; border-top: 2px solid #7B61FF; padding: 14px 16px; border-radius: 6px; margin-bottom: 12px; }
    .news-title { color: #F5F5F5; font-size: 15px; font-weight: 500; margin-bottom: 6px; }
    .news-meta { color: #888; font-size: 12px; }

    .asset-label { display: inline-block; padding: 0; border: none; background: transparent; color: #F5F5F5; font-size: 22px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; }

    div[data-testid="stFileUploader"] small { display: none; }

    .section-divider { height: 1px; background: #1E1E1E; margin: 14px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

nav, asset_type, period, horizon, run_models = render_sidebar()

if nav == "Assets":
    st.markdown("<div class='asset-label'>Assets</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ticker", value="", placeholder="Enter a Stock")
    ticker_file = st.file_uploader("Ticker file", type=["txt", "csv"])

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    ticker = ticker_input.upper().strip()
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

    last_close = float(data["Close"].iloc[-1])
    prev_close = float(data["Close"].iloc[-2]) if len(data) > 1 else last_close
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100 if prev_close else 0.0
    change_text = f"{change:+.2f} ({pct_change:+.2f}%)"

    st.markdown(
        f"""
        <div class="price-header">
            <div class="ticker">{ticker}</div>
            <div class="price">${last_close:,.2f}</div>
            <div class="badge">{change_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            label="Download",
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
