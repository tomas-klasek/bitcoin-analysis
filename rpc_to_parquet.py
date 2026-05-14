from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd
import time
import os

def save_checkpoint():
    pd.DataFrame(blocks).to_parquet("blocks_backup.parquet")
    pd.DataFrame(transactions).to_parquet("transactions_backup.parquet")
    print("Backup saved")

rpc_user = "bitcoin"
rpc_password = "btc_analysis"

rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=1200)

info = rpc.getblockchaininfo()
prune_height = info["pruneheight"]
latest = rpc.getblockcount()
prune_target_size = info["prune_target_size"]

blocks_parquet = "blocks_3.0.parquet"
transactions_parquet = "transactions.parquet"

if os.path.exists(blocks_parquet):
    df_blocks = pd.read_parquet(blocks_parquet)
    prune_height = df_blocks["height"].max() + 1
    

print("Prune target size: ", prune_target_size)
print("Start: ", prune_height)
print("End: ", latest)
print("Number of blocks: ", latest - prune_height, "\n\n")


blocks = []
transactions = []

for h in range(prune_height, latest+1):
    try:
        curr = rpc.getblock(rpc.getblockhash(h), 2)
        if h % 10 == 0:
            print(f"Progress:  {(h - prune_height) / (latest - prune_height + 1) * 100:.2f} %")
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
                       "version" : curr["version"]
                       })
        
        for tx in curr["tx"]:
            fee = tx.get("fee", None)
            vsize = tx.get("vsize", None)
            transactions.append({"height" : h,
                                 "txid" : tx["txid"],
                                 "fee" : fee,
                                 "vsize" : vsize              
                })
        
        if h % 100 == 0:
            save_checkpoint()
        
    #Block not available 
    except Exception as e:
        print("Skipped block ", h, "\nError message: ", str(e))
        time.sleep(1)
        continue
    
print("Finished!")
df = pd.DataFrame(blocks)    
df_tx = pd.DataFrame(transactions)

df.to_parquet(blocks_parquet)
df_tx.to_parquet(transactions_parquet)

   

