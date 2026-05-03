import streamlit as st


def render_sidebar():
    st.sidebar.header("Navigation")
    nav = st.sidebar.radio("Go to", ["Assets", "Mutual Funds"])

    asset_type = "Stocks"
    period = "2y"
    horizon = 5
    run_models = False

    if nav == "Assets":
        st.sidebar.subheader("Assets")
        asset_type = st.sidebar.selectbox("Asset type", ["Stocks", "ETFs"])
        period = st.sidebar.selectbox("Data period", ["6mo", "1y", "2y", "5y", "max"], index=2)

        st.sidebar.subheader("Prediction")
        horizon = st.sidebar.slider("Forecast horizon (days)", 1, 30, 5)
        run_models = st.sidebar.button("Run Forecast Models")

    if nav == "Mutual Funds":
        st.sidebar.subheader("Mutual Funds")
        st.sidebar.caption("SIP calculator available")

    return nav, asset_type, period, horizon, run_models
