import streamlit as st


def render_sidebar():
    st.sidebar.markdown("<div class='sidebar-title brand-title'>APEX CAPITAL</div>", unsafe_allow_html=True)
    nav = st.sidebar.radio("", ["Assets", "Mutual Funds"], label_visibility="collapsed")
    st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    asset_type = "Stocks"
    period = "2y"
    horizon = 5
    run_models = False

    if nav == "Assets":
        st.sidebar.markdown("<div class='sidebar-section'>Asset</div>", unsafe_allow_html=True)
        asset_type = st.sidebar.selectbox("Asset type", ["Stocks", "ETFs"])
        period = st.sidebar.selectbox("Data period", ["6mo", "1y", "2y", "5y", "max"], index=2)
        st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        st.sidebar.markdown("<div class='sidebar-section'>Prediction</div>", unsafe_allow_html=True)
        horizon = st.sidebar.slider("Forecast horizon (days)", 1, 30, 5)
        run_models = st.sidebar.button("Run Forecast Models")
        st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    if nav == "Mutual Funds":
        st.sidebar.markdown("<div class='sidebar-section'>Mutual Funds</div>", unsafe_allow_html=True)
        st.sidebar.caption("SIP calculator available")
        st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    return nav, asset_type, period, horizon, run_models
