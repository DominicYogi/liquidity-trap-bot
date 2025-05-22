def find_trap_zones(df, buffer_pct=0.05):
    highs = df['high']
    lows = df['low']
    trap_zones = []

    for i in range(10, len(df)):
        recent_highs = highs[i-10:i]
        recent_lows = lows[i-10:i]

        highest_high = recent_highs.max()
        lowest_low = recent_lows.min()

        # Trap above equal highs
        similar_highs = recent_highs[(recent_highs > highest_high * (1 - buffer_pct)) & 
                                     (recent_highs < highest_high * (1 + buffer_pct))]
        if len(similar_highs) >= 2:
            trap_zones.append({'type': 'stop-above-high', 'price': highest_high})

        # Trap below equal lows
        similar_lows = recent_lows[(recent_lows > lowest_low * (1 - buffer_pct)) & 
                                   (recent_lows < lowest_low * (1 + buffer_pct))]
        if len(similar_lows) >= 2:
            trap_zones.append({'type': 'stop-below-low', 'price': lowest_low})

    return trap_zones
