def find_trap_zones(df, wick_tolerance=0.1, min_touches=3):
    wick_points = []

    for i in range(1, len(df)-1):
        high = df.loc[i, "high"]
        low = df.loc[i, "low"]
        open_price = df.loc[i, "open"]
        close_price = df.loc[i, "close"]

        # Upper wick
        body_top = max(open_price, close_price)
        if high - body_top > wick_tolerance:
            wick_points.append(high)

        # Lower wick
        body_bottom = min(open_price, close_price)
        if body_bottom - low > wick_tolerance:
            wick_points.append(low)

    wick_points.sort()
    trap_zones = []

    if not wick_points:
        return trap_zones

    # Group similar wick levels
    cluster = [wick_points[0]]
    for price in wick_points[1:]:
        if abs(price - cluster[-1]) <= wick_tolerance:
            cluster.append(price)
        else:
            if len(cluster) >= min_touches:
                trap_zones.append(sum(cluster) / len(cluster))
            cluster = [price]
    if len(cluster) >= min_touches:
        trap_zones.append(sum(cluster) / len(cluster))

    return trap_zones
