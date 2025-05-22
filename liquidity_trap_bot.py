import requests
import pandas as pd
from datetime import datetime
import time

# ====== CONFIGURATION =======
API_KEY = "B7S360OVQWAXAU6K"  # Your Alpha Vantage API key here
FROM_SYMBOL = "EUR"  # Change to "USD" for USDCAD
TO_SYMBOL = "USD"    # Change to "CAD" for USDCAD
INTERVAL = "15min"   # Alpha Vantage supports 1min, 5min, 15min, 30min, 60min
MIN_TOUCHES = 2      # Minimum touches to confirm trap zone
WICK_TOLERANCE = 0.1 # How close wick needs to be to consider (as fraction of candle size)

# Alpha Vantage rate limits: max 5 calls/min, so wait 12s between calls if needed
RATE_LIMIT_WAIT = 12

# ===========================

def fetch_forex_data(from_symbol, to_symbol, interval, api_key):
    """
    Fetch forex OHLC data from Alpha Vantage.
    Returns pandas DataFrame with timestamp, open, high, low, close columns.
    """
    print(f"Fetching {from_symbol}{to_symbol} data from Alpha Vantage...")
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
        print("API Error or limit reached:", data.get("Note", data))
        return None

    ts = data[key]
    df = pd.DataFrame.from_dict(ts, orient="index")
    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close"
    })
    # Convert columns to float
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    # Convert index to datetime and sort ascending
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.reset_index(inplace=True)
    df.rename(columns={"index": "timestamp"}, inplace=True)

    print(f"Fetched {len(df)} candles.")
    return df

def identify_wick_points(df, wick_tolerance=0.1):
    """
    Identify candle wicks (upper or lower shadows) that may form liquidity traps.
    Returns list of wick prices (either highs or lows) that are significant.
    wick_tolerance: fraction of candle size that qualifies as wick.
    """
    wick_points = []
    for _, row in df.iterrows():
        candle_size = row["high"] - row["low"]
        if candle_size == 0:
            continue  # skip flat candles

        upper_wick = row["high"] - max(row["open"], row["close"])
        lower_wick = min(row["open"], row["close"]) - row["low"]

        # Check if upper wick is significant
        if upper_wick >= wick_tolerance * candle_size:
            wick_points.append(row["high"])

        # Check if lower wick is significant
        elif lower_wick >= wick_tolerance * candle_size:
            wick_points.append(row["low"])

    return wick_points

def find_trap_zones(df, wick_tolerance=0.1, min_touches=2):
    """
    Cluster wick points into zones where price touched multiple times (liquidity traps).
    Returns list of tuples: (zone_price, number_of_touches)
    """
    wick_points = identify_wick_points(df, wick_tolerance)
    if not wick_points:
        return []

    wick_points = sorted(wick_points)

    trap_zones = []
    cluster = [wick_points[0]]

    for price in wick_points[1:]:
        # If price is close to cluster center (within tolerance), add to cluster
        cluster_mean = sum(cluster) / len(cluster)
        if abs(price - cluster_mean) <= wick_tolerance * cluster_mean:
            cluster.append(price)
        else:
            # Close cluster, if touches meet min requirement add zone
            if len(cluster) >= min_touches:
                zone_price = sum(cluster) / len(cluster)
                trap_zones.append((zone_price, len(cluster)))
            cluster = [price]

    # Check last cluster
    if len(cluster) >= min_touches:
        zone_price = sum(cluster) / len(cluster)
        trap_zones.append((zone_price, len(cluster)))

    return trap_zones

def generate_signals(df, trap_zones, tolerance=0.0005):
    """
    Generate buy/sell signals when price approaches trap zones.
    tolerance: how close price must be to trap zone to trigger signal.
    Returns list of dicts with timestamp, signal ('BUY' or 'SELL'), price.
    """
    signals = []
    for _, row in df.iterrows():
        price = row["close"]
        timestamp = row["timestamp"]

        for zone_price, touches in trap_zones:
            if abs(price - zone_price) <= tolerance:
                # Price near a trap zone
                # If price below zone, signal BUY (expect bounce)
                # If price above zone, signal SELL (expect rejection)
                if price < zone_price:
                    signals.append({"timestamp": timestamp, "signal": "BUY", "price": price})
                else:
                    signals.append({"timestamp": timestamp, "signal": "SELL", "price": price})
    return signals

def main():
    # Fetch data
    df = fetch_forex_data(FROM_SYMBOL, TO_SYMBOL, INTERVAL, API_KEY)
    if df is None:
        print("Failed to fetch data. Exiting.")
        return

    # Find liquidity trap zones
    trap_zones = find_trap_zones(df, wick_tolerance=WICK_TOLERANCE, min_touches=MIN_TOUCHES)
    if not trap_zones:
        print("No liquidity trap zones detected.")
    else:
        print(f"Detected {len(trap_zones)} liquidity trap zones:")
        for zone_price, touches in trap_zones:
            print(f" Zone around {zone_price:.5f} with {touches} touches")

    # Generate signals based on zones
    signals = generate_signals(df, trap_zones)
    if not signals:
        print("No trade signals generated.")
    else:
        print(f"Generated {len(signals)} trade signals:")
        for sig in signals:
            print(f" {sig['timestamp']} - {sig['signal']} at {sig['price']:.5f}")

if __name__ == "__main__":
    main()
