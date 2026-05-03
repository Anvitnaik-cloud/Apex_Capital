import streamlit as st
import plotly.graph_objects as go


def render_trend_metrics(data, ticker):
    st.subheader(f"{ticker} Trend Analysis")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=data["Date"], y=data["MA50"], name="MA 50"))
    fig.add_trace(go.Scatter(x=data["Date"], y=data["MA200"], name="MA 200"))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

    vol_fig = go.Figure()
    vol_fig.add_trace(go.Bar(x=data["Date"], y=data["Volume"], name="Volume"))
    vol_fig.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(vol_fig, use_container_width=True)
