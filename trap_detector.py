import numpy as np

def find_trap_zones(df, wick_tolerance=0.0015, min_touches=3):
    """
    Find liquidity trap zones based on wick clustering.

    wick_tolerance: max % difference to group touches
    min_touches: minimum number of wick touches to mark zone
    """

    highs = df['high'].values
    lows = df['low'].values

    trap_zones = []

    # Combine highs and lows for clustering
    wick_points = np.concatenate([highs, lows])

    # Sort wick points
    wick_points.sort()

    # Group wick points by closeness (within wick_tolerance)
    clusters = []
    cluster = [wick_points[0]]

    for price in wick_points[1:]:
        if abs(price - cluster[-1]) / cluster[-1] <= wick_tolerance:
            cluster.append(price)
        else:
            if len(cluster) >= min_touches:
                clusters.append(cluster)
            cluster = [price]
    # Check last cluster
    if len(cluster) >= min_touches:
        clusters.append(cluster)

    # Build trap zones from clusters (average price)
    for c in clusters:
        avg_price = np.mean(c)
        trap_zones.append({'price': avg_price, 'touches': len(c)})

    return trap_zones
