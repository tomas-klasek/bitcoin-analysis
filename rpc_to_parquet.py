from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd
import time
import os
import glob

rpc_user = "bitcoin"
rpc_password = "btc_analysis"

rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=1200)

info = rpc.getblockchaininfo()
start_height = info["pruneheight"]
latest = rpc.getblockcount()
prune_target_size = info["prune_target_size"]

blocks_parquet = "btc_analysis/blocks/blocks_3.0_new.parquet"
transactions_parquet = "btc_analysis/transactions_new.parquet"
 

#Checkpoints
os.makedirs("btc_analysis/blocks", exist_ok=True)
os.makedirs("btc_analysis/transactions", exist_ok=True)

block_files = sorted(glob.glob("btc_analysis/blocks/*"))
print("Files: ", block_files)

if len(block_files) != 0:
    latest_file = block_files[-1]
    latest_file = latest_file.replace(".parquet","")
    start_height = int(latest_file.split("_")[-1]) + 1
    
    

print("Prune target size: ", prune_target_size)
print("Start: ", start_height)
print("End: ", latest)
print("Number of blocks: ", latest - start_height, "\n\n")


blocks = []
transactions = []
batch_size = 300
batch_start = start_height

for h in range(start_height, latest+1):
    try:
        curr = rpc.getblock(rpc.getblockhash(h), 2)
        if (h - start_height) % 10 == 0:
            print(f"Progress:  {(h - start_height) / (latest - start_height + 1) * 100:.2f} %")
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
            
        if len(blocks) >= batch_size:
            batch_end = h
            blocks_filename = f"btc_analysis/blocks/blocks_{batch_start}_{batch_end}.parquet"
            pd.DataFrame(blocks).to_parquet(blocks_filename)
            
            transactions_filename = f"btc_analysis/transactions/transactions_{batch_start}_{batch_end}.parquet"
            pd.DataFrame(transactions).to_parquet(transactions_filename)

            print(f"Saved batch from {batch_start} to {batch_end}.")
            
            blocks = []
            transactions = []
            
            batch_start = h + 1
        
    #Block not available 
    except Exception as e:
        print("Skipped block ", h, "\nError message: ", str(e))
        time.sleep(1)
        continue

if len(blocks) > 0:
    batch_end = blocks[-1]["height"]
    blocks_filename = f"btc_analysis/blocks/blocks_{batch_start}_{batch_end}.parquet"
    pd.DataFrame(blocks).to_parquet(blocks_filename)
    
    transactions_filename = f"btc_analysis/transactions/transactions_{batch_start}_{batch_end}.parquet"
    pd.DataFrame(transactions).to_parquet(transactions_filename)

    print(f"Final batch saved from {batch_start} to {batch_end}.")
    
block_files = glob.glob("btc_analysis/blocks/*.parquet")

df_blocks = pd.concat(
    [pd.read_parquet(f) for f in block_files],
    ignore_index=True
)

transactions_files = glob.glob("btc_analysis/transactions/*.parquet")
df_tx = pd.concat(
    [pd.read_parquet(f) for f in transactions_files],
    ignore_index=True
)

df_blocks = df_blocks.sort_values("height")
df_tx = df_tx.sort_values(["height", "txid"])   

df_blocks.to_parquet(blocks_parquet)
df_tx.to_parquet(transactions_parquet)
print("Finished!")


   

