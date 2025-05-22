import streamlit as st
from price_fetcher import get_candles
from trap_detector import find_trap_zones
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Liquidity Trap Bot", layout="wide")
st.title("💥 Liquidity Trap Bot — Stop Hunt Detector")

symbol = st.selectbox("Symbol", ['BTCUSDT', 'ETHUSDT'])
interval = st.selectbox("Candle Interval", ['1m', '5m', '15m', '1h'])
buffer_pct = st.slider("Sensitivity (%)", 1, 10, 5) / 100
refresh_seconds = st.slider("Auto-refresh every (seconds)", 5, 60, 10)

# Auto-refresh every N seconds
count = st.experimental_get_query_params().get("count", [0])[0]
count = int(count) + 1
st.experimental_set_query_params(count=count)
st.experimental_rerun() if count % refresh_seconds == 0 else None

@st.cache_data(ttl=refresh_seconds)
def fetch_data():
    return get_candles(symbol, interval)

df = fetch_data()
traps = find_trap_zones(df, buffer_pct)

last_price = df['close'].iloc[-1]

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name='Price'
))

for trap in traps:
    color = 'red' if trap['type'] == 'stop-above-high' else 'green'
    fig.add_hline(y=trap['price'], line_color=color, annotation_text=trap['type'], opacity=0.4)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🧠 Trap Zones Detected & Signals")

signal_generated = False
for t in traps[-5:]:
    st.write(f"🔸 **{t['type']}** at ${t['price']:.2f}")
    if t['type'] == 'stop-above-high' and last_price < t['price']:
        st.success(f"⚠️ Possible Stop Hunt Above near ${t['price']:.2f} — Price below zone, watch for breakout")
        signal_generated = True
    elif t['type'] == 'stop-below-low' and last_price > t['price']:
        st.success(f"⚠️ Possible Stop Hunt Below near ${t['price']:.2f} — Price above zone, watch for breakdown")
        signal_generated = True

if not signal_generated:
    st.info("No active stop hunt signals detected at current price.")

