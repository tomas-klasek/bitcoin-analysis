import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import glob
import pandas as pd

def save_batch(l, name, batch_start, batch_end):
    path = f"{name}/{name}_{batch_start}_{batch_end}.parquet"
    pd.DataFrame(l).to_parquet(path, index=False)
    return []

def load_parquets(path):
    files_block = sorted(glob.glob(path+"*parquet"))
    blocks_list = [pd.read_parquet(f) for f in files_block]
    df = pd.concat(blocks_list, ignore_index=True)
    return df

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

# Function to create a 1D histogram
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
# =============================================================================
# Function to create a 2D histogram
# =============================================================================
def create_histogram2D(x, y, xtitle, ytitle, file, nbins=80, delete=True, **kwargs):
    plt.figure()
    x = np.asarray(x)
    y = np.asarray(y)
    
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    plt.hist2d(x, y, nbins, cmap="viridis", norm=LogNorm(), **kwargs)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)

    plt.colorbar(label="Counts")
    plt.savefig(file, dpi=300, bbox_inches="tight")
    
    if delete:
        plt.show()
# =============================================================================
def compare_thresh(high, low, x, y , xtitle, ytitle, high_file, low_file):
    create_plot(high[x], high[y], xtitle, ytitle, high_file, color="blue", s=1)
    create_plot(low[x], low[y], xtitle, ytitle, low_file, color="red", s=1)

def save_fig(path):
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()