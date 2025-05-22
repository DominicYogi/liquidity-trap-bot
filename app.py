import streamlit as st
from price_fetcher import get_candles
from trap_detector import find_trap_zones
from trade_simulator import simulate_trades
import plotly.graph_objects as go

st.set_page_config(page_title="Liquidity Trap Bot", layout="wide")
st.title("💥 Liquidity Trap Bot — Stop Hunt Detector & Simulator")

symbol = st.selectbox("Symbol", ['BTCUSDT', 'ETHUSDT'])
interval = st.selectbox("Candle Interval", ['1m', '5m', '15m', '1h'])
wick_tolerance = st.slider("Wick Clustering Tolerance (%)", 0.05, 1.0, 0.15) / 100
min_touches = st.slider("Min Wick Touches", 2, 5, 3)
stop_loss_pct = st.slider("Stop Loss (%)", 0.1, 5.0, 0.2) / 100
take_profit_pct = st.slider("Take Profit (%)", 0.1, 10.0, 0.4) / 100

with st.spinner("Fetching data..."):
    df = get_candles(symbol, interval)

trap_zones = find_trap_zones(df, wick_tolerance, min_touches)
trades = simulate_trades(df, trap_zones, stop_loss_pct, take_profit_pct)

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name='Price'
))

for zone in trap_zones:
    fig.add_hline(y=zone['price'], line_color='orange', annotation_text=f"Trap Zone ({zone['touches']} touches)", opacity=0.3)

for trade in trades:
    color = 'green' if trade['outcome'] == 'win' else 'red'
    fig.add_vline(x=trade['entry_time'], line_dash='dot', line_color=color)
    fig.add_vline(x=trade['exit_time'], line_dash='dash', line_color=color)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Simulated Trades")

if not trades:
    st.info("No simulated trades detected based on current parameters.")
else:
    wins = sum(t['outcome'] == 'win' for t in trades)
    losses = sum(t['outcome'] == 'loss' for t in trades)
    win_rate = wins / len(trades) * 100

    st.write(f"Total Trades: {len(trades)}")
    st.write(f"Wins: {wins}")
    st.write(f"Losses: {losses}")
    st.write(f"Win Rate: {win_rate:.2f}%")

    for i, trade in enumerate(trades[-10:]):
        st.write(f"{i+1}. {trade['outcome'].upper()} | Entry: {trade['entry_price']:.2f} at {trade['entry_time']} | Exit: {trade['exit_price']:.2f} at {trade['exit_time']} | Profit: {trade['profit']:.2f}")

