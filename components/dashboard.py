import streamlit as st
import plotly.graph_objects as go

from utils.indicators import compute_rsi, compute_macd


def render_dashboard(data, info, ticker):
    st.subheader(f"Dashboard: {ticker}")

    price_fig = go.Figure()
    price_fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Close",
            line=dict(color="#7B61FF", width=1),
        )
    )
    price_fig.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    price_fig.update_xaxes(showgrid=False, showline=False)
    price_fig.update_yaxes(showgrid=False, showline=True, linecolor="#1E1E1E")
    st.plotly_chart(price_fig, use_container_width=True)

    volume_fig = go.Figure()
    volume_fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
            line=dict(color="#888", width=1),
        )
    )
    volume_fig.update_layout(
        template="plotly_dark",
        height=240,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    volume_fig.update_xaxes(showgrid=False, showline=False)
    volume_fig.update_yaxes(showgrid=False, showline=True, linecolor="#1E1E1E")
    st.plotly_chart(volume_fig, use_container_width=True)

    rsi = compute_rsi(data["Close"]).iloc[-1]
    macd_line, macd_signal = compute_macd(data["Close"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P/E Ratio", info.get("trailingPE", "N/A"))
    col2.metric("Market Cap", info.get("marketCap", "N/A"))
    col3.metric("EPS", info.get("trailingEps", "N/A"))
    col4.metric("Dividend Yield", info.get("dividendYield", "N/A"))

    col5, col6 = st.columns(2)
    col5.metric("RSI", f"{rsi:.2f}")
    col6.metric("MACD", f"{macd_line.iloc[-1]:.2f}")

    st.subheader("Ownership Snapshot")
    st.write(
        {
            "Institutional Holders": info.get("heldPercentInstitutions", "N/A"),
            "Insider Holders": info.get("heldPercentInsiders", "N/A"),
            "Major Holders": info.get("heldPercentInstitutions", "N/A"),
        }
    )
