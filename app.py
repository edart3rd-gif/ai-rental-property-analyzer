import streamlit as st
import pandas as pd
import os
from openai import OpenAI

st.set_page_config(
    page_title="AI Rental Property Analyzer",
    page_icon="🏠"
)

st.title("🏠 AI Rental Property Analyzer")
st.write("Evaluate the financial potential of a rental property.")

st.header("Property Information")

purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=300000.0)
down_payment = st.number_input("Down Payment ($)", min_value=0.0, value=60000.0)
monthly_rent = st.number_input("Monthly Rent ($)", min_value=0.0, value=2500.0)
monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0.0, value=700.0)
interest_rate = st.number_input("Mortgage Interest Rate (%)", min_value=0.0, value=6.5)
loan_years = st.number_input("Loan Term (Years)", min_value=1, value=30)

# ---------- Analyze button ----------
if st.button("Analyze Property"):
    loan_amount = purchase_price - down_payment
    monthly_rate = interest_rate / 100 / 12
    number_payments = loan_years * 12

    if monthly_rate > 0:
        mortgage_payment = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** number_payments
            / ((1 + monthly_rate) ** number_payments - 1)
        )
    else:
        mortgage_payment = loan_amount / number_payments

    annual_rent = monthly_rent * 12
    annual_expenses = monthly_expenses * 12
    annual_mortgage = mortgage_payment * 12
    annual_cash_flow = annual_rent - annual_expenses - annual_mortgage

    cap_rate = ((annual_rent - annual_expenses) / purchase_price) * 100
    cash_on_cash = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0

    # Save everything so the AI button can use it later
    st.session_state["results"] = {
        "mortgage_payment": mortgage_payment,
        "annual_cash_flow": annual_cash_flow,
        "cap_rate": cap_rate,
        "cash_on_cash": cash_on_cash,
        "purchase_price": purchase_price,
        "down_payment": down_payment,
        "monthly_rent": monthly_rent,
        "monthly_expenses": monthly_expenses,
    }

# ---------- Show results if they exist ----------
if "results" in st.session_state:
    r = st.session_state["results"]

    st.header("📊 Investment Results")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Monthly Mortgage", f"${r['mortgage_payment']:,.2f}")
        st.metric("Annual Cash Flow", f"${r['annual_cash_flow']:,.2f}")
    with col2:
        st.metric("Cap Rate", f"{r['cap_rate']:.2f}%")
        st.metric("Cash-on-Cash Return", f"{r['cash_on_cash']:.2f}%")

    if r["cash_on_cash"] >= 8:
        st.success("🟢 Strong potential investment")
    elif r["cash_on_cash"] >= 4:
        st.warning("🟡 Moderate investment — analyze further")
    else:
        st.error("🔴 Weak cash flow based on these assumptions")

    st.header("📈 10-Year Projection")
    years = list(range(1, 11))
    cash_flows = [r["annual_cash_flow"]] * 10
    cumulative = [r["annual_cash_flow"] * y for y in years]

    projection = pd.DataFrame({
        "Year": years,
        "Annual Cash Flow": cash_flows,
        "Cumulative Cash Flow": cumulative
    })
    st.dataframe(projection, use_container_width=True)

    st.subheader("Cumulative Cash Flow")
    st.line_chart(projection.set_index("Year")[["Cumulative Cash Flow"]])

# ---------- AI Analysis button ----------
st.header("🤖 AI Investment Analysis")

if st.button("Generate AI Analysis"):
    if "results" not in st.session_state:
        st.warning("Please click **Analyze Property** first.")
    else:
        r = st.session_state["results"]

        prompt = f"""
Analyze this rental property as a real estate investment.

Purchase price: ${r['purchase_price']:,.0f}
Down payment: ${r['down_payment']:,.0f}
Monthly rent: ${r['monthly_rent']:,.0f}
Monthly expenses: ${r['monthly_expenses']:,.0f}
Mortgage payment: ${r['mortgage_payment']:,.0f}
Annual cash flow: ${r['annual_cash_flow']:,.0f}
Cap rate: {r['cap_rate']:.2f}%
Cash-on-cash return: {r['cash_on_cash']:.2f}%

Explain:
1. Whether the property appears financially attractive.
2. The biggest risks.
3. What the investor should investigate.
4. Give a final recommendation.

Do not present this as financial advice.
"""

        try:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",          # or "gpt-4o"
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)

        except Exception as e:
            st.warning(
                "AI analysis is not configured yet or the API key is missing. "
                "The financial calculations are still available."
            )
            st.caption(f"Error details: {e}")
