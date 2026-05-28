from utils import load_parquets

print("Loading transaction parquet...")
transactions_path = "transactions"
df_transactions = load_parquets(transactions_path)
print("Transaction parquet loaded.")

print("Creating utxo set...")
utxo = {}

for tx in df_transactions["txid"].to_dict("records"):

    # remove spent outputs
    for vin in tx["vin"]:
        if "coinbase" in vin:
            continue

        key = (vin["txid"], vin["vout"])
        utxo.pop(key, None)

    # add outputs
    for i, vout in enumerate(tx["vout"]):
        key = (tx["txid"], i)

        utxo[key] = {
            "value": vout["value"],
            "height": tx["height"]
        }

print(utxo)

