import streamlit as st
import plotly.graph_objects as go


def render_trend_metrics(data, ticker):
    st.subheader(f"{ticker} Trend Analysis")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Close",
            line=dict(color="#7B61FF", width=1),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, showline=False)
    fig.update_yaxes(showgrid=False, showline=True, linecolor="#1E1E1E")
    st.plotly_chart(fig, use_container_width=True)

    vol_fig = go.Figure()
    vol_fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
            line=dict(color="#888", width=1),
        )
    )
    vol_fig.update_layout(
        template="plotly_dark",
        height=220,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    vol_fig.update_xaxes(showgrid=False, showline=False)
    vol_fig.update_yaxes(showgrid=False, showline=True, linecolor="#1E1E1E")
    st.plotly_chart(vol_fig, use_container_width=True)
