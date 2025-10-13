"""
destripe.py
Includes function to reduce the striping effect of VisiumHD data.
Pre-processing using read_data functions is required.
Some functions are incorporated from bin2cell package.
"""
import numpy as np
import scanpy as sc

def destripe_b2c(sdata, quantile = 0.99, only_2um=True, plot=False):
    """
    function to destripe VisiumHD data using the method provided by bin2cell package.
    Note: bin2cell works on AnnData objects, which need to be extracted from spatialdata object.

    Correct the raw counts of the input object for known variable width of 
    VisiumHD 2um bins. Scales the total UMIs per bin on a per-row and 
    per-column basis, dividing by the specified ``quantile``. The resulting 
    value is stored in ``.obs[factor_key]``, and is multiplied by the 
    corresponding total UMI ``quantile`` to get ``.obs[adjusted_counts_key]``.

    Args:
    sdata: the spatialdata object
    quantile: the quantile needed for destriping (default at 99% by b2c)
    only2um: a boolean parameter to indicate whether only 2um bins are de-striped. default to True.
    (Future work to add de-striping to 8um and 16um bins)
    plot: whether to generate summary plots (not yet implemented)

    Return:
    sdata: the resulting spatialdata object
    """
    def destripe(adata, quantile=0.99, counts_key="n_counts", factor_key="destripe_factor",
                 adjusted_counts_key="n_counts_adjusted", adjust_counts=True):
        """
        Perform destriping calculations.
        Args:
        adata: 2um bin output (AnnData)
        quantile: quantile required for destriping (default = 0.99)
        counts_key: name of column with raw counts per bin (default = n_counts)
        factor_key: name of column to hold computed factor prior to reversing to count space (default = destripe_factor)
        adjusted_counts_key: name of column for storing destriped counts per bin (default = n_counts_adjusted)
        adjust_counts: boolean, whether to use computed adjusted count total to adjust counts in adata.X (default = True)
        """
        # validity check
        if counts_key not in adata.obs:
            raise KeyError(f"'{counts_key}' not found in adata.obs. Available columns: {adata.obs.columns.tolist()}")
        
        # Row-wise normalization
        row_q = adata.obs.groupby("array_row")[counts_key].quantile(quantile) # get quantile per row
        adata.obs[factor_key] = adata.obs[counts_key] / adata.obs["array_row"].map(row_q) # divide by quantile
        # clean-up bad values
        adata.obs[factor_key] = adata.obs[factor_key].replace([np.inf, -np.inf], np.nan)
        adata.obs[factor_key] = adata.obs[factor_key].fillna(1.0)

        # Column-wise normalization
        col_q = adata.obs.groupby("array_col")[factor_key].quantile(quantile)
        adata.obs[factor_key] /= adata.obs["array_col"].map(col_q)
        # clean-up bad values
        adata.obs[factor_key] = adata.obs[factor_key].replace([np.inf, -np.inf], np.nan)
        adata.obs[factor_key] = adata.obs[factor_key].fillna(1.0)
        
        # Global adjustment (global quantile * destripe factor)
        global_q = np.quantile(adata.obs[counts_key], quantile)
        adata.obs[adjusted_counts_key] = adata.obs[factor_key] * global_q
        # Adjust count matrix
        if adjust_counts:
            destripe_counts(adata, counts_key, adjusted_counts_key)
    
    def destripe_counts(adata, counts_key="n_counts", adjusted_counts_key="n_counts_adjusted"):
        """
        Scale each row (bin) of adata.X to have adjusted total counts.
        Args:
        adata: 2um bin output (AnnData)
        counts_key: name of column with raw counts per bin
        adjusted_counts_key: name of column storing the destriped counts per bin
        """
        #scanpy's utility function to make sure the anndata is not a view
        #if it is a view then weird stuff happens when you try to write to its .X
        sc._utils.view_to_actual(adata)
        # adjust count matrix
        scaling_factors = (adata.obs[adjusted_counts_key] / adata.obs[counts_key]).replace([np.inf, -np.inf], np.nan).fillna(1.0) # handle bad values (NaN, inf, -inf), define scaling factor = 1
        adata.X = adata.X.multiply(scaling_factors.values[:, None]) # matrix multiplication, edited for efficiency
        adata.obs[counts_key] = np.array(adata.X.sum(axis=1)).flatten() # edit n_counts based on destriped counts

    if only_2um: # only handling 2um
        key = "square_002um"
        if key not in sdata.tables: # double check if key is present
            raise KeyError(f"{key} not found in sdata.tables")
        adata = sdata.tables[key]
        adata.obs["n_counts"] = np.array(adata.X.sum(axis=1)).flatten() # compute n_counts
        destripe(adata, quantile=quantile)
        sdata.tables[key] = adata  # update modified table back

    return sdata