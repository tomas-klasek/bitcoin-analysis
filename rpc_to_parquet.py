from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd
import time

rpc_user = "bitcoin"
rpc_password = "btc_analysis"

rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=600)

prune_height = rpc.getblockchaininfo()["pruneheight"]
latest = rpc.getblockcount()

print("Start: ", prune_height)
print("End: ", latest)
print("Number of blocks: ", latest - prune_height, "\n\n")

time.sleep(5)

blocks = []

for h in range(prune_height, latest+1):
    try:
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
    #Block not available 
    except Exception as e:
        print("Skipped block ", h, "\nError message: ", str(e))
        time.sleep(5)
        continue
    
print("Finished!")
df = pd.DataFrame(blocks)

df.to_parquet("blocks_1.0.parquet")
   

