import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("blocks.parquet")

df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["ntx"]/df["dt_sec"]
#df["size_mb"] = df["size"] / 1e6
#df["tx_density"] = df["ntx"]/df["size_mb"]

print()
df.head()
df.info()
df.describe()
print()

print(df)

plt.ticklabel_format(useOffset=False)
plt.plot(df["height"], df["nTxpertime"])
plt.xlabel("Block height")
plt.ylabel("Number of transactions per second")
plt.yscale("log")
plt.savefig("plots/block_transactions.png", dpi=300, bbox_inches="tight")
plt.show()

