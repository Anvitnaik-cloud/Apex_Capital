import streamlit as st
import pandas as pd


def render_sip_calculator():
    st.subheader("SIP Calculator")

    monthly = st.number_input("Monthly Investment", min_value=100.0, value=5000.0, step=100.0)
    rate = st.number_input("Expected Annual Return (%)", min_value=1.0, value=12.0, step=0.5)
    years = st.number_input("Time Period (years)", min_value=1, value=10, step=1)

    months = int(years * 12)
    monthly_rate = rate / 100 / 12

    balance = 0.0
    balances = []
    for m in range(1, months + 1):
        balance = (balance + monthly) * (1 + monthly_rate)
        balances.append({"Month": m, "Value": balance})

    total_invested = monthly * months
    returns = balance - total_invested

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested", f"{total_invested:,.2f}")
    col2.metric("Estimated Returns", f"{returns:,.2f}")
    col3.metric("Final Value", f"{balance:,.2f}")

    df = pd.DataFrame(balances)
    st.line_chart(df.set_index("Month"), use_container_width=True)
