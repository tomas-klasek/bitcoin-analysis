import numpy as np
import matplotlib.pyplot as plt


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
def compare_thresh(high, low, x, y , xtitle, ytitle, high_file, low_file, scatter = True, logx=False, logy=False, xlim=None, delete=True, **kwargs):
    create_plot(high[x], high[y], xtitle, ytitle, high_file, color="blue", s=1)
    create_plot(low[x], low[y], xtitle, ytitle, low_file, color="blue", s=1)

def save_fig(path):
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()