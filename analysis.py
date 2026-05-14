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
    
def create_histogram(x, title, file, logy=False, bins=100):
    plt.figure()
    #plt.ticklabel_format(useOffset=False)
    plt.hist(x, bins)
    plt.xlabel(title)
    if logy == True:
        plt.yscale("log")

    plt.savefig(file, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()
    
def bits_to_target(bits_hex):
    #bits = int(bits_hex, 16)
    bits=bits_hex
    exponent = bits >> 24
    mantissa = bits & 0xffffff

    target = mantissa * (1 << (8 * (exponent - 3)))

    return target
    
    
df = pd.read_parquet("blocks_prices.parquet")
df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["nTx"]/df["dt_sec"]
df["size_mb"] = df["size"] / 1e6
df["tx_density"] = df["nTx"]/df["size_mb"]


#df["target_dec"] = bits_to_target(df["target"])

print()
#df.head()
#df.info()
#df.describe()
print(df["target"].describe())


create_plot(df["height"], df["nTxpertime"], "Block height", "Number of transactions per second", "plots/block_transactions.png", False)
create_plot(df["height"], df["dt_sec"], "Block height", "Time since last block", "plots/block_timeElapsed.png")
create_plot(df["nTx"], df["dt_sec"], "Number of transactions", "Time since last block", "plots/ntx_vs_dt.png")
create_plot(df["height"], df["price"], "Height", "Price [USD]", "plots/block_price.png")
create_plot(df["nTx"], df["price"], "Number of transactions in a block", "Price [USD]", "plots/ntx_price.png")
create_plot(df["height"], df["tx_density"], "Block height", "Transaction density", "plots/block_tx_density.png")
create_plot(df["height"], df["size_mb"], "Block height", "Size [MB]", "plots/block_size.png")

create_histogram(df["dt_sec"], "Time since last block", "plots/hist_dt_sec.png")
create_histogram(df["size_mb"], "Block size in MB", "plots/hist_size.png")
create_histogram(df["tx_density"], "Transaction density", "plots/hist_tx_dens.png")

