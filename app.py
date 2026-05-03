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

    .github-float { position: fixed; top: 96px; right: 48px; z-index: 9999; pointer-events: auto; }
    .github-link { display: inline-flex; align-items: center; gap: 10px; padding: 10px 18px; border: 1px solid #E6E6E6; border-radius: 8px; background: #FFFFFF; color: #000; text-decoration: none; font-size: 13px; font-weight: 600; letter-spacing: 0.2px; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18); }
    .github-link:visited { color: #000; }
    .github-link:hover, .github-link:active, .github-link:focus { background: #FFFFFF; border-color: #E6E6E6; color: #000; }
    .github-link svg { width: 18px; height: 18px; fill: #0F0F0F; }

    @media (max-width: 640px) {
        .github-float { top: 80px; right: 28px; }
    }

    .section-divider { height: 1px; background: #1E1E1E; margin: 14px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

nav, asset_type, period, horizon, run_models = render_sidebar()

st.markdown(
    """
    <div class='github-float'>
        <a class='github-link' href='https://github.com/Anvitnaik-cloud/Apex_Capital/fork' target='_blank'>
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 0.5c-6.63 0-12 5.37-12 12 0 5.3 3.438 9.8 8.207 11.387.6.11.793-.26.793-.577 0-.285-.01-1.04-.016-2.04-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.757-1.333-1.757-1.09-.745.083-.73.083-.73 1.205.085 1.84 1.238 1.84 1.238 1.07 1.835 2.807 1.305 3.492.997.108-.776.418-1.305.762-1.605-2.665-.303-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.236-3.22-.124-.303-.536-1.523.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.29-1.552 3.296-1.23 3.296-1.23.655 1.653.243 2.873.12 3.176.77.84 1.234 1.91 1.234 3.22 0 4.61-2.806 5.624-5.479 5.92.43.37.814 1.102.814 2.222 0 1.604-.015 2.896-.015 3.286 0 .32.192.694.8.576 4.765-1.59 8.2-6.086 8.2-11.384 0-6.63-5.37-12-12-12z" />
            </svg>
            Fork
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

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
