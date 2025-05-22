import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from trap_detector import find_trap_zones, generate_signals

st.set_page_config(page_title="Liquidity Trap Bot", layout="wide")

API_KEY = "B7S360OVQWAXAU6K"

@st.cache_data(ttl=600)
def fetch_forex_data(from_symbol, to_symbol, interval, api_key):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "interval": interval,
        "apikey": api_key,
        "outputsize": "compact"
    }
    response = requests.get(url, params=params)
    data = response.json()

    key = f"Time Series FX ({interval})"
    if key not in data:
        st.error(f"API Error or Rate Limit: {data.get('Note', data)}")
        return None

    ts = data[key]
    df = pd.DataFrame.from_dict(ts, orient="index")
    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close"
    })

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.reset_index(inplace=True)
    df.rename(columns={"index": "timestamp"}, inplace=True)
    return df

def plot_candles(df, trap_zones, signals):
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Candles"
    )])

    # Plot trap zones as horizontal lines
    for zone in trap_zones:
        fig.add_hline(y=zone, line_color='red', line_dash='dash', annotation_text='Trap Zone', annotation_position="top left")

    # Plot signals as scatter
    for sig in signals:
        color = 'green' if sig['signal'] == 'BUY' else 'red'
        fig.add_trace(go.Scatter(
            x=[sig['timestamp']],
            y=[sig['price']],
            mode='markers',
            marker=dict(color=color, size=12, symbol='triangle-up' if sig['signal'] == 'BUY' else 'triangle-down'),
            name=f"{sig['signal']} Signal"
        ))

    fig.update_layout(
        title="Liquidity Trap Zones & Signals",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("Liquidity Trap Bot")

    col1, col2 = st.columns(2)
    with col1:
        symbol_option = st.selectbox("Select Forex Pair", options=["EURUSD", "USDCAD"])
        interval = st.selectbox("Select Interval", options=["5min", "15min", "30min"], index=1)
    with col2:
        wick_tolerance = st.slider("Wick Tolerance (%)", 1, 20, 10) / 100
        min_touches = st.slider("Min Touches for Zone", 1, 5, 2)
        signal_tolerance = st.slider("Signal Proximity Tolerance (pips)", 1, 20, 5) / 10000

    from_symbol = symbol_option[:3]
    to_symbol = symbol_option[3:]

    if st.button("Run Liquidity Trap Detection"):
        df = fetch_forex_data(from_symbol, to_symbol, interval, API_KEY)
        if df is not None:
            trap_zones = find_trap_zones(df, wick_tolerance=wick_tolerance, min_touches=min_touches)
            st.write(f"Detected {len(trap_zones)} Liquidity Trap Zones.")
            signals = generate_signals(df, trap_zones, tolerance=signal_tolerance)
            st.write(f"Generated {len(signals)} Trade Signals.")

            plot_candles(df, trap_zones, signals)

if __name__ == "__main__":
    main()
