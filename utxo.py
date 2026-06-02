from utils import load_parquets
import pandas as pd
import os
import matplotlib.pyplot as plt
import glob

save_path = "utxo/utxo_all.parquet"

print("Loading input and output parquets...")
inputs_path = "inputs/"
outputs_path = "outputs/"

# inputs = load_parquets(inputs_path)
outputs = load_parquets(outputs_path)
print("Input and output parquets loaded.")


print("Creating utxo set...")
utxo = {}

# outputs = outputs[outputs["height"] == 946675]
# inputs = inputs[inputs["height"] == 946675]

# len_inputs = len(inputs)
len_outputs = len(outputs)


# print("Check dropna: ", len(inputs), " ", len(outputs))
# inputs = inputs.dropna(subset=["prev_txid", "prev_vout"])
outputs = outputs.dropna(subset=["txid", "vout", "height", "value"])
# print("Check dropna: ", len(inputs), " ", len(outputs))

# outputs["vout"] = outputs["vout"].astype("int64")
# inputs["prev_vout"] = inputs["prev_vout"].astype("int64")

# outputs["txid"] = outputs["txid"].astype(str)
# inputs["prev_txid"] = inputs["prev_txid"].astype(str)

outputs_map = {
    (txid, vout): (value, height)
    for txid, vout, value, height in outputs.itertuples(index=False)
}



for i, tx in outputs.iterrows():
    if i % 10000 == 0:
        print(f"Crea    ting TXO rogress:  {i / len_outputs * 100:.2f} %")
    if i > 100000:
        break
    key = (tx["txid"], tx["vout"])
    
    utxo[key] = {
        "value": tx["value"],
        "height": tx["height"]
    }

print(len(utxo))


# for i, tx in inputs.iterrows():
#     if i % 10000 == 0:
#         print(f"Removing spent TXO progress:  {i / len_inputs * 100:.2f} %")
#     if i > 100000:
#         break
#     key = (tx["prev_txid"], tx["prev_vout"])
#     utxo.pop(key, None)


print("UTXO set created!")
print("Creating dataframe...")
print(len(utxo))
rows = []
for (txid, vout), data in utxo.items():
    rows.append({
            "txid" : txid,
            "vout" : vout,
            "value" : data["value"],
            "height" : data["height"]
        })

df_utxo = pd.DataFrame(rows)
os.makedirs("utxo", exist_ok=True)
df_utxo.to_parquet(save_path)

tx_values = outputs.groupby("txid")["value"].sum()

avg = tx_values.mean()
print("Average transaction value: ", avg)

print("Number of zeros: ", (df_utxo["value"] == 0).sum())
print("Number of all: ", (outputs["value"] != 0).sum())
print("Head: ",df_utxo["value"].head())
print("Median: ",df_utxo["value"].median())
print("Mean: ",df_utxo["value"].mean())
print("Sum: ",df_utxo["value"].sum())

g = df_utxo.groupby("height")["value"].mean()
print(g.head())
print(len(g))

df_utxo["is_zero"] = df_utxo["value"] == 0

zero_rate = df_utxo.groupby("height")["is_zero"].mean()

plt.plot(zero_rate.index, zero_rate.values)
plt.show()

