import streamlit as st
import plotly.graph_objects as go
from data_fetcher import fetch_forex_data
from trap_detector import find_trap_zones

st.set_page_config(layout="wide")
st.title("💥 Liquidity Trap Detector Bot")

# User controls
symbol = st.selectbox("Choose Forex Pair", ["EUR/USD", "USD/CAD"])
interval = st.selectbox("Candle Interval", ["1min", "5min", "15min"])
wick_tolerance = st.slider("Wick Tolerance", 0.01, 0.5, 0.1, 0.01)
min_touches = st.slider("Minimum Touches", 2, 10, 3)

# Fetch data
try:
    df = fetch_forex_data(symbol=symbol, interval=interval, outputsize=100)
    trap_zones = find_trap_zones(df, wick_tolerance, min_touches)

    # Plot
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    for zone in trap_zones:
        fig.add_hline(y=zone, line_color="red", line_dash="dash", annotation_text=f"Trap Zone: {zone:.4f}")

    fig.update_layout(title=f"{symbol} Chart with Trap Zones", xaxis_title="Time", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
