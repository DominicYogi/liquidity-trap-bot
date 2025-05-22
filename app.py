import streamlit as st
from price_fetcher import get_candles
from trap_detector import find_trap_zones
import plotly.graph_objects as go

st.set_page_config(page_title="Liquidity Trap Bot", layout="wide")
st.title("💥 Liquidity Trap Bot — Stop Hunt Detector")

symbol = st.selectbox("Symbol", ['BTCUSDT', 'ETHUSDT'])
interval = st.selectbox("Candle Interval", ['1m', '5m', '15m', '1h'])
buffer_pct = st.slider("Sensitivity (%)", 1, 10, 5) / 100

with st.spinner("Fetching data..."):
    df = get_candles(symbol, interval)
    traps = find_trap_zones(df, buffer_pct)

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name='Price'
))

# Mark trap zones
for trap in traps:
    color = 'red' if trap['type'] == 'stop-above-high' else 'green'
    fig.add_hline(y=trap['price'], line_color=color, annotation_text=trap['type'], opacity=0.4)

st.plotly_chart(fig, use_container_width=True)

if traps:
    st.subheader("🧠 Trap Zones Detected")
    for t in traps[-5:]:
        st.write(f"🔸 **{t['type']}** at ${t['price']:.2f}")
else:
    st.info("No strong trap zones found yet. Wait for market structure to form.")
