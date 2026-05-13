from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd

rpc_user = "bitcoin"
rpc_password = "btc_analysis"

rpc = AuthServiceProxy(
    f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=600
)

prune_height = rpc.getblockchaininfo()["pruneheight"]
latest = rpc.getblockcount()

blocks = []

print("Progress: ")

for h in range(prune_height, latest+1):
    curr = rpc.getblock(rpc.getblockhash(h), 1)
    print(f"Progress:  {(h - prune_height) / (latest + 1 - prune_height) * 100:.2f} %")
    blocks.append({"height" : h,
                   "time": curr["time"],
                   "nTx" : curr["nTx"],
                   "size" : curr["size"],
                   "target" : curr["target"],
                   "chainwork" : curr["chainwork"],
                   "difficulty" : curr["difficulty"],
                   "nonce" : curr["nonce"],
                   "mediantime" : curr["mediantime"],
                   "weight" : curr["weight"],
                   "version" : curr["version"],                  
                   })

df = pd.DataFrame(blocks)

df.to_parquet("blocks_1.0.parquet")
   

