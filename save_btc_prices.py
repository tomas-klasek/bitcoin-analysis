import requests
import pandas as pd
import glob

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

#Loading the block and transaction parquets
# =============================================================================
block_dir = "blocks/"

files_block = sorted(glob.glob(block_dir+"*parquet"))

blocks_list = [pd.read_parquet(f) for f in files_block]

df_blocks = pd.concat(blocks_list, ignore_index=True)

# =============================================================================

prices = []
for i, r in enumerate(df_blocks.itertuples(), start=1):
    
    curr_t = r.time
    curr_price = get_prices(curr_t)

    if i % 10 == 0:
        print(f"Progress:  {(i) / (len(df_blocks)) * 100:.2f} %")

    prices.append({"height" : r.height,
                      "price" : curr_price,
                      "time" : curr_t})
        
df_prices = pd.DataFrame(prices)
df_prices.to_parquet("btc_prices.parquet")




