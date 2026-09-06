import streamlit as st

st.title("🏠 AI Rental Property Analyzer")

st.write(
    "Analyze the potential profitability of a rental property."
)

purchase_price = st.number_input(
    "Purchase Price ($)",
    min_value=0.0,
    value=300000.0
)

monthly_rent = st.number_input(
    "Monthly Rent ($)",
    min_value=0.0,
    value=2500.0
)

monthly_expenses = st.number_input(
    "Monthly Expenses ($)",
    min_value=0.0,
    value=700.0
)

if st.button("Analyze Property"):

    annual_rent = monthly_rent * 12
    annual_expenses = monthly_expenses * 12

    annual_cash_flow = annual_rent - annual_expenses

    cap_rate = (
        annual_cash_flow / purchase_price
    ) * 100

    st.subheader("Investment Results")

    st.metric(
        "Annual Cash Flow",
        f"${annual_cash_flow:,.2f}"
    )

    st.metric(
        "Cap Rate",
        f"{cap_rate:.2f}%"
    )

    if cap_rate >= 7:
        st.success("Strong investment opportunity")
    elif cap_rate >= 5:
        st.warning("Potential investment — analyze further")
    else:
        st.error("Weak investment based on these numbers")
