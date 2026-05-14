import requests
import pandas as pd


def get_prices(ts):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "startTime": ts * 1000,
        "limit": 1
    }

    r = requests.get(url, params=params)
    data = r.json()

    if len(data) == 0:
        return None

    # close price
    return float(data[0][4])


df_rpc = pd.read_parquet("blocks_1.0.parquet")

prices = []

for i, r in enumerate(df_rpc.itertuples(), start=1):
    
    curr_t = r.time
    curr_price = get_prices(curr_t)

    if i % 10 == 0:
        print(f"Progress:  {(i) / (len(df_rpc)) * 100:.2f} %")
        print(curr_price)


    prices.append({"height" : r.height,
                      "price" : curr_price,
                      "time" : curr_t})
        
df_prices = pd.DataFrame(prices)
df_prices.to_parquet("btc_prices.parquet")

# df_prices = pd.read_parquet("btc_prices.parquet")
df_final = df_rpc.merge(df_prices[["height", "price"]], on="height", how="left")
df_final.to_parquet("blocks_prices.parquet")



