import requests
import pandas as pd

API_KEY = "83849ffdf30d4c088096c83887b4ff76"

def fetch_forex_data(symbol="EUR/USD", interval="1min", outputsize=100):
    symbol_encoded = symbol.replace("/", "%2F")
    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol={symbol_encoded}&interval={interval}"
        f"&outputsize={outputsize}&apikey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise Exception(f"Error fetching data: {data}")

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={
        "datetime": "timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close"
    })

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float
    })

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df
