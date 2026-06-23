from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd
import time
import os
import glob
from utils import save_batch

rpc_user = "bitcoin"

rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=1200)

info = rpc.getblockchaininfo()
start_height = info["pruneheight"]
latest = rpc.getblockcount()
prune_target_size = info["prune_target_size"]


#Checkpoints
os.makedirs("blocks", exist_ok=True)
os.makedirs("transactions", exist_ok=True)
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


block_files = sorted(glob.glob("blocks/*"))
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
inputs = []
outputs = []
batch_size = 200
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
            
            for vin in tx["vin"]:
                if "coinbase" in vin:
                    continue
                
                inputs.append({"height" : h,
                               "prev_vout" : vin["vout"],
                               "prev_txid" : vin["txid"],
                               "txid" : tx["txid"]})
                
            for i, vout in enumerate(tx["vout"]):
                outputs.append({"height" : h,
                                "vout" : i,
                                "value_sat" : ["value"],
                                "txid" : tx["txid"]})
            
        if len(blocks) >= batch_size:
            batch_end = h
            
            blocks = save_batch(blocks, "blocks", batch_start, batch_end)
            transactions = save_batch(transactions, "transactions", batch_start, batch_end)
            inputs = save_batch(inputs, "inputs", batch_start, batch_end)
            outputs = save_batch(outputs, "outputs", batch_start, batch_end)

            print(f"Saved batch from {batch_start} to {batch_end}.")
            
            batch_start = h + 1
            
            # To deal with losing connection to RPC after batch saving
            rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332", timeout=1200)
            
    #Block not available 
    except Exception as e:
        print("Skipped block ", h, "\nError message: ", str(e))
        time.sleep(1)
        continue

if len(blocks) > 0:
    batch_end = blocks[-1]["height"]

    save_batch(blocks, "blocks", batch_start, batch_end)
    save_batch(transactions, "transactions", batch_start, batch_end)
    save_batch(inputs, "inputs", batch_start, batch_end)
    save_batch(outputs, "outputs", batch_start, batch_end)

    print(f"Final batch saved from {batch_start} to {batch_end}.")
    
print("Finished!")


   

