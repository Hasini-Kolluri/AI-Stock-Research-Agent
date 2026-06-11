"""
Stock Research Agent using Gemini + Yahoo Finance.

Provides comprehensive stock analysis:
- Real-time stock data
- Financial metrics
- Analyst ratings
- AI-powered investment summary
"""

import argparse
import os

from dotenv import load_dotenv

load_dotenv()

# ==========================
# API KEY HANDLING
# ==========================

try:
    import streamlit as st

    GOOGLE_API_KEY = st.secrets.get(
        "GOOGLE_API_KEY",
        os.getenv("GOOGLE_API_KEY")
    )

except Exception:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. "
        "Add it to .env or Streamlit Secrets."
    )

# ==========================
# YFINANCE
# ==========================

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def get_stock_data(ticker: str) -> dict:

    if not HAS_YFINANCE:
        return {
            "ticker": ticker,
            "error": "yfinance not installed"
        }

    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker,
        "name": info.get("longName", ticker),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "price": info.get(
            "currentPrice",
            info.get("regularMarketPrice", 0)
        ),
        "market_cap": info.get("marketCap", 0),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "forward_pe": info.get("forwardPE", "N/A"),
        "peg_ratio": info.get("pegRatio", "N/A"),
        "revenue_growth": info.get("revenueGrowth", "N/A"),
        "profit_margin": info.get("profitMargins", "N/A"),
        "dividend_yield": info.get("dividendYield", 0),
        "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
        "analyst_rating": info.get(
            "recommendationKey",
            "N/A"
        ),
        "target_price": info.get(
            "targetMeanPrice",
            "N/A"
        ),
        "description": info.get(
            "longBusinessSummary",
            ""
        )[:1000],
    }


def analyze_stock(data: dict) -> str:

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    stock_info = "\n".join(
        f"{k}: {v}"
        for k, v in data.items()
        if k != "description"
    )

    messages = [
        SystemMessage(
            content=(
                "You are a professional financial analyst.\n\n"
                "Provide:\n"
                "1. Investment Thesis (2-3 sentences)\n"
                "2. Key Strengths (3 bullet points)\n"
                "3. Key Risks (3 bullet points)\n"
                "4. Valuation Assessment\n"
                "5. Verdict (Buy/Hold/Sell)\n\n"
                "Keep the response under 300 words."
            )
        ),
        HumanMessage(
            content=(
                f"Analyze this stock:\n\n"
                f"{stock_info}\n\n"
                f"Company Description:\n"
                f"{data.get('description', 'N/A')}"
            )
        )
    ]

    response = llm.invoke(messages)
    return response.content


def format_number(n):

    if isinstance(n, (int, float)):

        if n >= 1e12:
            return f"${n / 1e12:.2f}T"

        if n >= 1e9:
            return f"${n / 1e9:.2f}B"

        if n >= 1e6:
            return f"${n / 1e6:.2f}M"

        return f"${n:.2f}"

    return str(n)


def get_stock_history(ticker):

    stock = yf.Ticker(ticker)

    return stock.history(
        period="1y"
    )


def research_stock(ticker):

    data = get_stock_data(ticker)

    analysis = analyze_stock(data)

    history = get_stock_history(ticker)

    return data, analysis, history


def main():

    parser = argparse.ArgumentParser(
        description="Stock Research Agent"
    )

    parser.add_argument(
        "--ticker",
        required=True,
        help="Stock ticker symbol"
    )

    args = parser.parse_args()

    print(f"\n📈 Researching {args.ticker}...\n")

    data = get_stock_data(args.ticker)

    print("=" * 60)
    print(
        f"📊 {data.get('name', args.ticker)} "
        f"({args.ticker})"
    )
    print("=" * 60)

    print(
        f"Price: ${data.get('price', 'N/A')} | "
        f"Market Cap: {format_number(data.get('market_cap', 0))}"
    )

    print(
        f"Sector: {data.get('sector')} | "
        f"Industry: {data.get('industry')}"
    )

    print(
        f"P/E: {data.get('pe_ratio')} | "
        f"Forward P/E: {data.get('forward_pe')}"
    )

    print(
        f"52W Range: "
        f"${data.get('52w_low')} - "
        f"${data.get('52w_high')}"
    )

    analyst_rating = data.get("analyst_rating") or "N/A"

    print(
        f"Analyst: {str(analyst_rating).upper()} | "
        f"Target: ${data.get('target_price', 'N/A')}"
    )

    print("\n🤖 AI Analysis:")
    print("-" * 40)

    analysis = analyze_stock(data)

    print(analysis)


if __name__ == "__main__":
    main()