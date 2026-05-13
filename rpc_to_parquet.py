from bitcoinrpc.authproxy import AuthServiceProxy
import pandas as pd

rpc_user = "bitcoin"
rpc_password = "btc_analysis"

rpc = AuthServiceProxy(
    f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332"
)

prune_height = rpc.getblockchaininfo()["pruneheight"]

blocks = []

for h in range(prune_height, prune_height+10):
    curr = rpc.getblock(rpc.getblockhash(h))
    
    blocks.append({"height" : h, "time": curr["time"], "ntx" : curr["nTx"]})#, "size" : curr["size"], "target" : curr["target"]})

df = pd.DataFrame(blocks)

df.to_parquet("blocks.parquet")
df = pd.read_parquet("blocks.parquet")
   

