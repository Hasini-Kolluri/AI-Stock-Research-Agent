import streamlit as st
from agent import research_stock, format_number

st.set_page_config(
    page_title="AI Stock Research Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Stock Research Agent")
st.write("Analyze stocks using Yahoo Finance and Gemini AI")

ticker = st.text_input(
    "Enter Stock Ticker",
    placeholder="AAPL"
)

if st.button("Analyze"):


    if not ticker.strip():
        st.warning("Please enter a stock ticker.")
        st.stop()

    try:
        with st.spinner("Researching stock..."):
            data, analysis = research_stock(ticker)


        st.subheader("📊 Stock Metrics")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Price",
            f"${data['price']}"
        )

        col2.metric(
            "P/E Ratio",
            data["pe_ratio"]
        )

        col3.metric(
            "Market Cap",
            format_number(data["market_cap"])
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Forward P/E",
            data["forward_pe"]
        )

        target_price = data["target_price"]

        if isinstance(target_price, (int, float)):
            target_price = f"${target_price:.2f}"

        col2.metric(
            "Target Price",
            target_price
        )

        col3.metric(
            "Analyst Rating",
            str(data["analyst_rating"]).upper()
        )

        st.divider()


        with st.expander("🏢 Company Overview"):
            st.write(data["description"])


        st.subheader("🤖 AI Analysis")
        st.markdown(analysis)

    except Exception as e:
        st.error(f"Error: {e}")