import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from scipy.stats import expon

# Function to create a scatter plot
# =============================================================================
def create_plot(x, y , xtitle, ytitle, file, scatter = True, logx=False, logy=False, xlim=None, delete=True, **kwargs):
    plt.figure()
    #plt.ticklabel_format(useOffset=False)
    if scatter:
        plt.scatter(x, y, **kwargs)
    else:
        plt.plot(x, y, **kwargs)
    
    if xlim != None:
        plt.xlim(xlim)
    
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    
    if logx == True:
        plt.xscale("log")
    if logy == True:
        plt.yscale("log")

    plt.savefig(file, dpi=300, bbox_inches="tight")
    if delete:
        plt.show()

# =============================================================================

# Function to create a histogram
# =============================================================================
def create_histogram(x, xtitle, ytitle, file, logx=False, logy=False, nbins=100, xlim=None, logx_bins=False, delete=True, **kwargs):
    plt.figure()
    #plt.ticklabel_format(useOffset=False)
    if logx_bins:
        bins = np.logspace(0, 8, num=nbins)
    else:
        bins = nbins

    plt.hist(x, bins, **kwargs)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    if xlim != None:
        plt.xlim(xlim)
    
    
    if logx == True:
        plt.xscale("log")
    
    if logy == True:
        plt.yscale("log")

    plt.savefig(file, dpi=300, bbox_inches="tight")
    
    if delete:
        plt.show()
    #plt.close()
# =============================================================================

#Loading the block and transaction parquets
# =============================================================================
block_dir = "blocks/"
transaction_dir = "transactions/"

files_block = sorted(glob.glob(block_dir+"*parquet"))
files_transaction = sorted(glob.glob(transaction_dir+"*parquet"))

blocks_list = [pd.read_parquet(f) for f in files_block]
transaction_list = [pd.read_parquet(f) for f in files_transaction]

df_blocks = pd.concat(blocks_list, ignore_index=True)
df_transactions = pd.concat(transaction_list, ignore_index=True)

# =============================================================================

df = df_blocks    
df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["nTx"]/df["dt_sec"]
df["size_mb"] = df["size"] / 1e6
df["tx_density"] = df["nTx"]/df["size_mb"]
df_transactions["fee"] = (df_transactions["fee"].astype(float)*100000000.)

df["dt_rolling"] = df["dt_sec"].rolling(100).mean()
df["epoch"] = df["height"] // 2016
# =============================================================================




print("Printing info about the DataFrames:")
print("Block DataFrame:")
df.head()
df.info()
df.describe()

print("\n\nTransaction DataFrame:")
df_transactions.head()
df_transactions.info()
df_transactions.describe()


print("\nFee information:\n", df_transactions["fee"].describe())


create_plot(df["height"], df["nTxpertime"], "Block height", "Number of transactions per second", "plots/block_transactions.png", color="blue", s=5)
create_plot(df["height"], df["dt_sec"], "Block height", "Time since last block", "plots/block_timeElapsed.png", color="blue", s=5)
create_plot(df["nTx"], df["dt_sec"], "Number of transactions", "Time since last block", "plots/ntx_vs_dt.png", color="blue", s=5)
#create_plot(df["height"], df["price"], "Height", "Price [USD]", "plots/block_price.png")
#create_plot(df["nTx"], df["price"], "Number of transactions in a block", "Price [USD]", "plots/ntx_price.png")
create_plot(df["height"], df["tx_density"], "Block height", "Transaction density", "plots/block_tx_density.png",color="blue", s=5)
create_plot(df["height"], df["size_mb"], "Block height", "Size [MB]", "plots/block_size.png", color="blue", s=5)
#create_plot(df_transactions["height"], df_transactions["fee"], "Block height", "Fee", "plots/block_fee.png")


# Time between blocks and the Poisson fit
# ============================================================================= 
create_histogram(df["dt_sec"], "Time since last block", "Entries", "plots/hist_dt_sec.png", color="purple", density=True, delete=False)

data = df["dt_sec"].dropna().values
loc, scale = expon.fit(data, floc=0) #floc = fix location - at 0
x = np.linspace(0, data.max(), 1000)
lambda_par = 1/scale
pdf = lambda_par * np.exp(-lambda_par * x)
plt.plot(x, pdf, linewidth=3, label="Exponential fit", color="orange")

print("\nThe lambda parameter from the Poisson distribution fit: ", round(lambda_par,5))
print("\nMean block lifetime: ", round(scale,2))
plt.legend()
plt.show()
# =============================================================================

# Rolling mean and the vertical line corresponding to the difficulty adjustment
# ============================================================================= 
create_plot(df["height"], df["dt_rolling"], "Block height", "Rolling mean over 100 blocks", "plots/dt_rolling.png",delete=False,color="blue", s=5)

for h in df["height"]:
    if h % 2016 == 0:
        plt.axvline(h, color="red", label="Difficulty target change")
plt.legend()
plt.show()

print("Mean times over the epochs analysed: ", df.groupby("epoch")["dt_sec"].mean())

plt.figure()
for epoch, df_epoch in df.groupby("epoch"):
    plt.scatter(df_epoch["height"], df_epoch["dt_sec"].rolling(100, min_periods=20).mean(), s=5, label=f"Epoch: {epoch}")
plt.axhline(600, color="black", label="Target: 600s")
plt.legend()
plt.show()
# =============================================================================

create_histogram(df["size_mb"], "Block size in MB", "Entries", "plots/hist_size.png", color="purple")
create_histogram(df["tx_density"], "Transaction density", "Entries", "plots/hist_tx_dens.png", color="purple")
create_histogram(df_transactions["fee"], "Fee", "Entries", "plots/hist_fee.png", True, True, logx_bins=True, xlim=(1, 1e8), color="purple")
create_histogram(df_transactions["vsize"], "Virtual size of transaction", "Entries", "plots/hist_vsize.png", True, True, logx_bins=True, color="purple")
