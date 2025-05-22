import pandas as pd

def identify_wick_points(df, wick_tolerance=0.1):
    wick_points = []
    for _, row in df.iterrows():
        candle_size = row["high"] - row["low"]
        if candle_size == 0:
            continue

        upper_wick = row["high"] - max(row["open"], row["close"])
        lower_wick = min(row["open"], row["close"]) - row["low"]

        if upper_wick >= wick_tolerance * candle_size:
            wick_points.append(row["high"])
        elif lower_wick >= wick_tolerance * candle_size:
            wick_points.append(row["low"])

    return wick_points

def find_trap_zones(df, wick_tolerance=0.1, min_touches=2):
    wick_points = identify_wick_points(df, wick_tolerance)
    if not wick_points:
        return []

    wick_points = sorted(wick_points)

    trap_zones = []
    cluster = [wick_points[0]]

    for price in wick_points[1:]:
        cluster_mean = sum(cluster) / len(cluster)
        if abs(price - cluster_mean) <= wick_tolerance * cluster_mean:
            cluster.append(price)
        else:
            if len(cluster) >= min_touches:
                zone_price = sum(cluster) / len(cluster)
                trap_zones.append(zone_price)
            cluster = [price]

    if len(cluster) >= min_touches:
        zone_price = sum(cluster) / len(cluster)
        trap_zones.append(zone_price)

    return trap_zones

def generate_signals(df, trap_zones, tolerance=0.0005):
    signals = []
    for _, row in df.iterrows():
        price = row["close"]
        timestamp = row["timestamp"]

        for zone_price in trap_zones:
            if abs(price - zone_price) <= tolerance:
                if price < zone_price:
                    signals.append({"timestamp": timestamp, "signal": "BUY", "price": price})
                else:
                    signals.append({"timestamp": timestamp, "signal": "SELL", "price": price})
    return signals
