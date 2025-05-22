def simulate_trades(df, trap_zones, stop_loss_pct=0.002, take_profit_pct=0.004):
    """
    Simulate trades that enter when price sweeps below/above trap zones.

    stop_loss_pct: max loss % from entry price
    take_profit_pct: target gain % from entry price

    Returns list of trade dicts with entry, exit, profit, and outcome.
    """

    trades = []

    close_prices = df['close'].values
    timestamps = df['timestamp'].values

    for zone in trap_zones:
        zone_price = zone['price']
        entered = False
        entry_idx = None

        for i in range(1, len(close_prices)):
            price = close_prices[i]
            prev_price = close_prices[i-1]

            # Check for sweep: price crosses zone price downward or upward
            if not entered:
                if prev_price > zone_price and price <= zone_price:
                    # Short stop hunt
                    entered = True
                    entry_idx = i
                    entry_price = price
                    stop_loss = entry_price * (1 + stop_loss_pct)
                    take_profit = entry_price * (1 - take_profit_pct)
                    direction = 'short'

                elif prev_price < zone_price and price >= zone_price:
                    # Long stop hunt
                    entered = True
                    entry_idx = i
                    entry_price = price
                    stop_loss = entry_price * (1 - stop_loss_pct)
                    take_profit = entry_price * (1 + take_profit_pct)
                    direction = 'long'

            else:
                # Check exit conditions
                if direction == 'long':
                    if price <= stop_loss:
                        trades.append({'entry_time': timestamps[entry_idx], 'exit_time': timestamps[i], 'entry_price': entry_price, 'exit_price': price, 'profit': price - entry_price, 'outcome': 'loss'})
                        break
                    elif price >= take_profit:
                        trades.append({'entry_time': timestamps[entry_idx], 'exit_time': timestamps[i], 'entry_price': entry_price, 'exit_price': price, 'profit': price - entry_price, 'outcome': 'win'})
                        break
                else:  # short
                    if price >= stop_loss:
                        trades.append({'entry_time': timestamps[entry_idx], 'exit_time': timestamps[i], 'entry_price': entry_price, 'exit_price': price, 'profit': entry_price - price, 'outcome': 'loss'})
                        break
                    elif price <= take_profit:
                        trades.append({'entry_time': timestamps[entry_idx], 'exit_time': timestamps[i], 'entry_price': entry_price, 'exit_price': price, 'profit': entry_price - price, 'outcome': 'win'})
                        break

    return trades
