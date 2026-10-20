import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Stock Watch", layout="centered")
st.title("📱 My Stock Watcher")

tickers_input = st.text_input(
    "Stocks to watch (use .NS for Indian stocks):",
    "RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, AAPL"
)

def check_stock(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price = float(latest['Close'])
        rsi = float(latest['RSI'])

        signal = "🟡 WAIT / HOLD"
        reason = "Price is normal right now."

        if rsi <= 35 or (float(prev['SMA20']) <= float(prev['SMA50']) and float(latest['SMA20']) > float(latest['SMA50'])):
            signal = "🟢 BUY NOW"
            reason = "Stock is on sale or starting to climb up!"
        elif rsi >= 65 or (float(prev['SMA20']) >= float(prev['SMA50']) and float(latest['SMA20']) < float(latest['SMA50'])):
            signal = "🔴 SELL NOW"
            reason = "Stock is getting pricey or starting to drop!"

        return {"Stock": symbol, "Price": round(price, 2), "RSI": round(rsi, 1), "Signal": signal, "Why": reason}
    except Exception:
        return None

if st.button("🔄 Check My Stocks Now", use_container_width=True):
    symbols = [s.strip().upper() for s in tickers_input.split(",") if s.strip()]
    with st.spinner("Checking live stock prices..."):
        for sym in symbols:
            info = check_stock(sym)
            if info:
                with st.container(border=True):
                    st.subheader(f"{info['Stock']} — ₹/$ {info['Price']}")
                    st.markdown(f"### {info['Signal']}")
                    st.caption(f"{info['Why']} (RSI Score: {info['RSI']})")
