import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import expon
import scipy.stats as st
import seaborn as sns
from utils import load_parquets, create_plot, create_histogram, create_histogram2D, compare_thresh, save_fig
    
# Loading blocks, transaction and price parquets
# =============================================================================
block_dir = "blocks/"
transaction_dir = "transactions/"

df_blocks = load_parquets(block_dir)
df_transactions = load_parquets(transaction_dir)
df_prices = pd.read_parquet("btc_prices.parquet")

df_blocks = df_blocks.merge(df_prices[["height", "price"]], on="height", how="left")
# =============================================================================

# Calculating variables
# =============================================================================
df = df_blocks    
df = df.sort_values("time")

df["datetime"] = pd.to_datetime(df["time"], unit = "s")
df["dt"] = df["datetime"].diff()
df["dt_sec"] = df["dt"].dt.total_seconds()
df["nTxpertime"] = df["nTx"]/df["dt_sec"]
df["size_mb"] = df["size"] / 1e6
df["saturation"] = df["weight"]/4e6
df["nTx_next"] = df["nTx"].shift(-1)
df["dt_rolling"] = df["dt_sec"].rolling(100, min_periods=20).mean()
df["epoch"] = df["height"] // 2016

df_transactions["vsize_mb"] = df_transactions["vsize"]/1e6
df_transactions["fee"] = (df_transactions["fee"].astype(float)*100000000.) #btc to sat
df_transactions["fee_rate"] = df_transactions["fee"]/df_transactions["vsize"]

block_stats = df_transactions.groupby("height").agg({ 
    "fee": ["sum", "mean"],
    "fee_rate": ["mean", "median"],
    "vsize": ["sum", "mean", "median"]
    })

#val_mean_block = df_transactions.groupby("height")["value"].mean()
#val_median_block = df_transactions.groupby("height")["value"].median()
# =============================================================================

# =============================================================================
# Analysis part
# =============================================================================

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
save_fig("plots/poisson.png")
# =============================================================================

# Rolling mean and the vertical line corresponding to the difficulty adjustment, epoch analysis
# ============================================================================= 
create_plot(df["height"], df["dt_rolling"], "Block height", "Block lifetime rolling mean over 100 blocks", "plots/dt_rolling.png",delete=False,color="blue", s=5)

for h in df["height"]:
    if h % 2016 == 0:
        plt.axvline(h, color="red", label="Difficulty target change")
plt.legend()
save_fig("plots/height_lra.png")

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
save_fig("plots/height_lra_epochs.png")

epoch_stats = df.groupby("epoch")["dt_sec"].agg(["mean", "std", "count"])

print("\nEpoch stats:\n", epoch_stats)

# =============================================================================

# Creating histograms of basic quantities
# =============================================================================
create_histogram(df["nTx"], "Transactions per block", "Entries", "plots/hist_ntx.png", color="purple")
create_histogram(df["size_mb"], "Block size in MB", "Entries", "plots/hist_size.png", color="purple")
create_histogram(df_transactions["fee"], "Fee [sat]", "Entries", "plots/hist_fee.png", True, True, logx_bins=True, xlim=(1, 1e8), color="purple")
create_histogram(block_stats["fee_rate"]["mean"], "Fee rate mean per block [sat]", "Entries", "plots/hist_fee_rate_mean.png", color="purple")
create_histogram(block_stats["fee_rate"]["median"], "Fee rate median per block [sat]", "Entries", "plots/hist_fee_rate_mean.png", color="purple")

# Creating plots of basic quantities depending on height
# =============================================================================
create_plot(df["height"], block_stats["vsize"]["sum"], "Block height","Sum of virtual size per block [mb]", "plots/virt_size_sum.png", color="blue", s=1)
create_plot(df["height"], block_stats["vsize"]["mean"], "Block height","Mean of virtual size per block [b]", "plots/virt_size_mean.png", logy=True, color="blue", s=1)
create_plot(df["height"], block_stats["vsize"]["median"], "Block height","Median of virtual size per block [b]", "plots/virt_size_median.png", logy=True, color="blue", s=1)
create_plot(df["height"], block_stats["fee"]["mean"],  "Block height", "Fee mean per block [sat]", "plots/heigh_fee_mean.png", color="blue", s=1)
create_plot(df["height"], block_stats["fee_rate"]["mean"],  "Block height", "Fee rate mean per block [sat]", "plots/heigh_fee_rate_mean.png", color="blue", s=1)
create_plot(df["height"], block_stats["fee_rate"]["median"],  "Block height", "Fee rate median per block [sat]", "plots/heigh_fee_median.png", color="blue", s=1)
create_plot(df["height"], block_stats["fee_rate"]["mean"]/block_stats["fee_rate"]["median"], "Block height", "Fee rate mean/median [sat]", "plots/fee_rate_mean-median_rat.png",color="blue", s=1)
create_plot(df["height"], df["saturation"], "Block height", "Block fill ratio", "plots/block_saturation.png", color="blue", s=1)
#create_plot(df["height"], df["nTxpertime"].rolling(100).sum()/df["dt_sec"].rolling(100).sum(), "Block height", "Number of transactions per second", "plots/block_transactions.png", color="blue", s=1)
create_plot(df["height"], df["dt_sec"], "Block height", "Time since last block", "plots/block_timeElapsed.png", color="blue", s=1)
create_plot(df["height"], df["price"], "Height", "Price [USD]", "plots/block_price.png", scatter=False, color="blue")
create_plot(df["height"], df["size_mb"], "Block height", "Size [MB]", "plots/block_size.png", color="blue", s=1)

# Creating plots of other depencencies
# =============================================================================
create_histogram2D(df["price"], block_stats["fee_rate"]["median"], "Price [USD]", "Fee rate median per block", "plots/price_vs_fee_rate_median.png")

create_histogram2D(df["dt_sec"], block_stats["fee"]["mean"],  "Time since last block [s]", "Fee mean per block [sat]", "plots/dt_fee_mean.png")
create_histogram2D(df["dt_sec"], block_stats["fee_rate"]["mean"],  "Time since last block [s]", "Fee rate mean per block [sat]", "plots/dt_fee_rate_mean.png")
create_histogram2D(df["dt_sec"], block_stats["fee_rate"]["median"],  "Time since last block [s]", "Fee rate median per block [sat]", "plots/dt_fee_median.png")

create_histogram2D(df["nTx"], df["price"], "Number of transactions in a block", "Price [USD]", "plots/ntx_price.png")
create_histogram2D(df["nTx"], block_stats["fee_rate"]["median"],  "nTx", "Fee rate median per block [sat]", "plots/nTx_fee_median.png")
create_histogram2D(df["nTx"], df["dt_sec"], "Number of transactions", "Time since last block", "plots/ntx_vs_dt.png")
create_histogram2D(df["nTx_next"], df["dt_sec"], "Number of transactions", "Previous block time", "plots/ntx_vs_dt.png")

create_plot(df["saturation"], block_stats["fee_rate"]["median"],  "Block fill ratio", "Fee rate median per block [sat]", "plots/saturation_fee_median.png", color="blue", s=1)

# Fee above threshold analysis
# =============================================================================
tx_block = df_transactions.groupby("height").agg(fee_rate_median = ("fee_rate", "median"), 
                                                 fee_rate_mean = ("fee_rate", "mean"),
                                                 tx_count = ("fee_rate", "size"))

df_merged = df.merge(tx_block, on="height", how="left")

threshold = df_merged["fee_rate_mean"].quantile(0.9)
high = df_merged[df_merged["fee_rate_mean"]>threshold]
low = df_merged[df_merged["fee_rate_mean"]<=threshold]

print("Fill ratio for fee rate above threshold: ", high["saturation"].mean())
print("Fill ratio for fee rate below threshold: ", low["saturation"].mean())

compare_thresh(high, low, "height", "fee_rate_median", "Block height", "Fee rate median [sat]", "plots/thresh_high_fee_rate_median.png" , "plots/thresh_low_fee_rate_median.png")
compare_thresh(high, low, "height", "dt_sec", "Block height", "Time since last block [s]", "plots/thresh_high_fee_rate_median.png", "plots/thresh_low_dt.png")
compare_thresh(high, low, "height", "saturation", "Block height", "Block fill ratio", "plots/thresh_high_fee_rate_median.png", "plots/thresh_low_fill_ratio.png")
compare_thresh(high, low, "height", "tx_count", "Block height", "Transaction count", "plots/thresh_high_fee_rate_median.png", "plots/thresh_low_fill_ratio.png")

# Creating correlation plot
# =============================================================================

df = df.merge(
    block_stats["fee_rate"]["median"].rename("fee_rate_median_block"),
    on="height",
    how="left"
)
df = df.merge(
    block_stats["vsize"]["sum"].rename("vsize_sum"),
    on="height",
    how="left"
)

df["prev_dt"] = df["dt_sec"].shift(1)
cols = ["prev_dt", "nTx", "vsize_sum", "price", "fee_rate_median_block"]

corr = df[cols].corr()
corr = df[cols].rename(columns={
    "fee_rate_median_block": "fee_med",
    "vsize_sum": "vsize"
}).corr()

print(corr)

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)

plt.title("Correlation heatmap")
plt.tight_layout()
plt.savefig("plots/correlation.png", dpi=300, bbox_inches="tight")
plt.show()








