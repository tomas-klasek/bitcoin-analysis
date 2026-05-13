import pandas as pd
import matplotlib.pyplot as plt

def create_plot(x, y , xtitle, ytitle, file, logy=False):
    plt.figure()
    #plt.ticklabel_format(useOffset=False)
    plt.scatter(x, y, color="red", s=5)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    if logy == True:
        plt.yscale("log")

    plt.savefig(file, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()
    
    
df = pd.read_parquet("blocks.parquet")
df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["ntx"]/df["dt_sec"]
#df["size_mb"] = df["size"] / 1e6
#df["tx_density"] = df["ntx"]/df["size_mb"]

print()
#df.head()
#df.info()
#df.describe()
print(df["dt_sec"].describe())


create_plot(df["height"], df["nTxpertime"], "Block height", "Number of transactions per second", "plots/block_transactions.png", False)
create_plot(df["height"], df["dt_sec"], "Block height", "Time since last block", "plots/block_timeElapsed.png")
create_plot(df["ntx"], df["dt_sec"], "Number of transactions", "Time since last block", "plots/block_timeElapsed.png")
create_plot(df["dt_sec"], df["ntx"], "Time since last block", "Number of transactions", "plots/block_timeElapsed.png")

df["dt_sec"].plot(kind="hist", bins=100)
plt.yscale("log")
