import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from scipy.stats import expon
import scipy.stats as st
import seaborn as sns
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

#Loading the block, transaction and price parquets
# =============================================================================
block_dir = "blocks/"
transaction_dir = "transactions/"

files_block = sorted(glob.glob(block_dir+"*parquet"))
files_transaction = sorted(glob.glob(transaction_dir+"*parquet"))

blocks_list = [pd.read_parquet(f) for f in files_block]
transaction_list = [pd.read_parquet(f) for f in files_transaction]

df_blocks = pd.concat(blocks_list, ignore_index=True)
df_transactions = pd.concat(transaction_list, ignore_index=True)

df_prices = pd.read_parquet("btc_prices.parquet")
df_blocks = df_blocks.merge(df_prices[["height", "price"]], on="height", how="left")

# =============================================================================

df = df_blocks    
df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["nTx"]/df["dt_sec"]
df["size_mb"] = df["size"] / 1e6
df_transactions["vsize_mb"] = df_transactions["vsize"]/1e6
vsize_mb_sum = df_transactions.groupby("height")["vsize_mb"].sum()
vsize_mb_mean = df_transactions.groupby("height")["vsize"].mean()
vsize_mb_median = df_transactions.groupby("height")["vsize"].median()

df["saturation"] = df["weight"]/4e6
#df["saturation"] = df["size_mb"]/4.

df["tx_density"] = df["nTx"]/df["size_mb"]
df_transactions["fee"] = (df_transactions["fee"].astype(float)*100000000.) #btc to sat

df["nTx_next"] = df["nTx"].shift(-1)

df["dt_rolling"] = df["dt_sec"].rolling(100, min_periods=20).mean()
df["epoch"] = df["height"] // 2016
df_transactions["fee_rate"] = df_transactions["fee"]/df_transactions["vsize"]

vsize_sum = df_transactions.groupby("height")["vsize"].sum()

df = df.merge(
    vsize_sum.rename("vsize_sum"),
    on="height",
    how="left"
)


fee_sum_block = df_transactions.groupby("height")["fee"].sum()
fee_mean_block = df_transactions.groupby("height")["fee"].mean()
fee_rate_mean_block = df_transactions.groupby("height")["fee_rate"].mean()
fee_rate_median_block = df_transactions.groupby("height")["fee_rate"].median()

df = df.merge(
    fee_rate_median_block.rename("fee_rate_median_block"),
    on="height",
    how="left"
)

#val_mean_block = df_transactions.groupby("height")["value"].mean()
#val_median_block = df_transactions.groupby("height")["value"].median()
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


create_plot(df["height"], df["nTxpertime"], "Block height", "Number of transactions per second", "plots/block_transactions.png", color="blue", s=1)
create_plot(df["height"], df["dt_sec"], "Block height", "Time since last block", "plots/block_timeElapsed.png", color="blue", s=1)
create_plot(df["nTx"], df["dt_sec"], "Number of transactions", "Time since last block", "plots/ntx_vs_dt.png", color="blue", s=1)
create_plot(df["nTx_next"], df["dt_sec"], "Number of transactions", "Lifetime of previous block", "plots/ntx_vs_dt.png", color="blue", s=1)


print("Correlation of dt and ntx:\n", df[["dt_sec", "nTx"]].corr())
print("Correlation of dt and next ntx:\n", df[["dt_sec", "nTx_next"]].corr())


create_plot(df["height"], df["price"], "Height", "Price [USD]", "plots/block_price.png", scatter=False, color="blue")
create_plot(df["nTx"], df["price"], "Number of transactions in a block", "Price [USD]", "plots/ntx_price.png", color="blue", s=1)
create_plot(df["height"], df["tx_density"], "Block height", "Transaction density", "plots/block_tx_density.png",color="blue", s=1)
create_plot(df["height"], df["size_mb"], "Block height", "Size [MB]", "plots/block_size.png", color="blue", s=1)
create_plot(df_transactions["height"], df_transactions["fee"], "Block height", "Fee", "plots/block_fee.png", color="blue", s=1)


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
plt.savefig("plots/poisson.png", dpi=300, bbox_inches="tight")
plt.show()
# =============================================================================

# Rolling mean and the vertical line corresponding to the difficulty adjustment, epoch analysis
# ============================================================================= 
create_plot(df["height"], df["dt_rolling"], "Block height", "Block lifetime rolling mean over 100 blocks", "plots/dt_rolling.png",delete=False,color="blue", s=5)

for h in df["height"]:
    if h % 2016 == 0:
        plt.axvline(h, color="red", label="Difficulty target change")
plt.legend()
plt.savefig("plots/height_lra.png", dpi=300, bbox_inches="tight")
plt.show()

print("Mean times over the epochs analysed: ", df.groupby("epoch")["dt_sec"].mean())

plt.figure()
for epoch, df_epoch in df.groupby("epoch"):
    plt.scatter(df_epoch["height"], df_epoch["dt_sec"].rolling(100, min_periods=20).mean(), s=5, label=f"Epoch: {epoch}")
    conf_int = st.t.interval(0.95, len(df_epoch), loc=df_epoch["dt_sec"].mean(), scale=df_epoch["dt_sec"].std() / np.sqrt(len(df_epoch)))
    print("Confidence interval: ", conf_int)
    print(f"Number of transactions in epoch {epoch}: {len(df_epoch['nTx'])}")
    
    
plt.axhline(600, color="black", label="Target: 600s")
plt.xlabel("Block height")
plt.ylabel("Block lifetime rolling average (100 blocks) [s]")
plt.legend()
plt.savefig("plots/height_lra_epochs.png", dpi=300, bbox_inches="tight")
plt.show()

epoch_stats = df.groupby("epoch")["dt_sec"].agg(["mean", "std", "count"])

print("\nEpoch stats:\n", epoch_stats)

# =============================================================================

create_histogram(df["size_mb"], "Block size in MB", "Entries", "plots/hist_size.png", color="purple")
create_histogram(df["tx_density"], "Transaction density", "Entries", "plots/hist_tx_dens.png", color="purple")
create_histogram(df_transactions["fee"], "Fee [sat]", "Entries", "plots/hist_fee.png", True, True, logx_bins=True, xlim=(1, 1e8), color="purple")
create_histogram(fee_mean_block, "Fee mean per block [sat]", "Entries", "plots/hist_fee_mean.png", color="purple")
create_histogram(fee_rate_mean_block, "Fee rate mean per block [sat]", "Entries", "plots/hist_fee_rate_mean.png", color="purple")

create_plot(df_transactions["height"], df_transactions["vsize_mb"], "Block height","Virtual size [mb]", "plots/virt_size_all.png", color="blue", s=1)
create_plot(df["height"], vsize_mb_sum, "Block height","Sum of virtual size per block [mb]", "plots/virt_size_sum.png", color="blue", s=1)
create_plot(df["height"], vsize_mb_mean, "Block height","Mean of virtual size per block [b]", "plots/virt_size_mean.png", color="blue", s=1)
create_plot(df["height"], vsize_mb_median, "Block height","Median of virtual size per block [b]", "plots/virt_size_median.png", color="blue", s=1)

create_plot(df["price"], fee_rate_median_block, "Price [USD]", "Fee rate median per block", "plots/price_vs_fee_rate_median.png", color="blue", s=1)

create_plot(df["dt_sec"], fee_mean_block,  "Time since last block [s]", "Fee mean per block [sat]", "plots/height_fee_mean.png", color="blue", s=1)
create_plot(df["dt_sec"], fee_rate_mean_block,  "Time since last block [s]", "Fee rate mean per block [sat]", "plots/height_fee_rate_mean.png", color="blue", s=1)
create_plot(df["dt_sec"], fee_rate_median_block,  "Time since last block [s]", "Fee rate median per block [sat]", "plots/height_fee_median.png", color="blue", s=1)

create_plot(df["height"], fee_mean_block,  "Block height", "Fee mean per block [sat]", "plots/dt_fee_mean.png", color="blue", s=1)
create_plot(df["height"], fee_rate_mean_block,  "Block height", "Fee rate mean per block [sat]", "plots/dt_fee_rate_mean.png", color="blue", s=1)
create_plot(df["height"], fee_rate_median_block,  "Block height", "Fee rate median per block [sat]", "plots/dt_fee_median.png", color="blue", s=1)

create_plot(df["saturation"], fee_rate_median_block,  "Block filling ratio", "Fee rate median per block [sat]", "plots/dt_fee_median.png", color="blue", s=1)

# Fee above threshold analysis
# =============================================================================
create_plot(df["height"], fee_rate_mean_block/fee_rate_median_block, "Block height", "Fee rate mean/median [sat]", "plots/thresh_fee_rate_mean-median_rat.png",color="blue", s=1)


tx_block = df_transactions.groupby("height").agg(fee_rate_median = ("fee_rate", "median"), 
                                                 fee_rate_mean = ("fee_rate", "mean"),
                                                 tx_count = ("fee_rate", "size"))

df_merged = df.merge(tx_block, on="height", how="left")

threshold = df_merged["fee_rate_mean"].quantile(0.9)
high = df_merged[df_merged["fee_rate_mean"]>threshold]
low = df_merged[df_merged["fee_rate_mean"]<=threshold]

print(high["saturation"].mean())
print(df["saturation"].mean())

create_plot(high["height"], high["fee_rate_median"], "Block height", "Fee rate median [sat]", "plots/thresh_high_fee_rate_median.png", color="blue", s=1)
create_plot(low["height"], low["fee_rate_median"], "Block height", "Fee rate median [sat]", "plots/thresh_low_fee_rate_median.png", color="red", s=1)

create_plot(high["height"], high["fee_rate_mean"], "Block height", "Fee rate mean [sat]", "plots/thresh_high_fee_rate_mean.png", color="blue", s=1)
create_plot(low["height"], low["fee_rate_mean"], "Block height", "Fee rate mean [sat]", "plots/thresh_low_fee_rate_mean.png", color="red", s=1)

create_plot(high["height"], high["price"], "Block height", "Price [USD]]", "plots/thresh_high_price.png", color="blue", s=1)
create_plot(low["height"], low["price"], "Block height", "Price [USD]", "plots/thresh_low_price.png", color="red", s=1)

create_plot(high["height"], high["dt_sec"], "Block height", "Time since last block [s]", "plots/thresh_high_dt.png",color="blue", s=1)
create_plot(low["height"], low["dt_sec"], "Block height", "Time since last block [s]", "plots/thresh_low_dt.png",color="red", s=1)

create_plot(high["height"], high["saturation"], "Block height", "Block filling ratio", "plots/thresh_high_fill_ratio.png",color="blue", s=1)
create_plot(low["height"], low["saturation"], "Block height", "Block filling ratio", "plots/thresh_low_fill_ratio.png",color="red", s=1)

create_plot(high["height"], high["tx_count"], "Block height", "Transaction count", "plots/thresh_high_fill_ratio.png",color="blue", s=1)
create_plot(low["height"], low["tx_count"], "Block height", "Transaction count", "plots/thresh_low_fill_ratio.png",color="red", s=1)

# =============================================================================


corr = df[["dt_sec", "nTx", "vsize_sum", "saturation", "fee_rate_median_block"]].corr()
print(corr)

cols = ["dt_sec", "nTx", "vsize_sum", "saturation", "price", "fee_rate_median_block"]

corr = df[cols].corr()

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)

plt.title("Correlation heatmap")
plt.tight_layout()
plt.savefig("plots/correlation.png", dpi=300, bbox_inches="tight")
plt.show()








