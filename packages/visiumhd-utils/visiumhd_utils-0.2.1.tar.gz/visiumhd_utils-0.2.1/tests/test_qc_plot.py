"""
This file heavily tests the compute_qc_metrics and plot_qc_metrics functions,
which are custom written and needed for other pipelines.
Other functions in qc_plot.py are wrappers of spatialdata_plot functions and are
not intensively tested.
"""
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from scipy.sparse import csr_matrix
import anndata as ad
import visiumhd_utils.qc_plot as qp

def sdata_test():
    """
    helper function to create a SpatialData object
    """
    barcodes = ["C0", "C1", "C2"]
    genes = ["G0", "G1", "MT-G2"] # includes mito gene
    X = csr_matrix([[1, 0, 0],
                    [2, 1, 0],
                    [3, 1, 2]]) 

    obs = pd.DataFrame(index=barcodes)
    var = pd.DataFrame(index=genes)

    adata = ad.AnnData(X, obs=obs, var=var)
    return SimpleNamespace(tables={"square_002um": adata})

def test_compute_qc_metrics():
    """test function for compute QC metrics"""
    sdata = sdata_test()
    qp.compute_qc_metrics(sdata, bin_size=2, mito_prefix="MT-")

    adata = sdata.tables["square_002um"]
    obs = adata.obs
    # check for required columns
    required = {"total_counts", "n_genes_by_counts", "pct_counts_mt", "log_total_counts"}
    assert required <= set(obs.columns)
    # check if log total counts is calculated correctly
    np.testing.assert_allclose(obs["log_total_counts"], np.log1p(obs["total_counts"]))
    # test if MT gene count is subset and calculated correctly
    mt_counts = np.array(adata.X[:, 2].todense()).flatten()  # MT-G2 gene counts
    total = np.array(obs["total_counts"])
    expected_pct = 100 * mt_counts / total
    np.testing.assert_allclose(obs["pct_counts_mt"], expected_pct) # check if every element is the same

def test_compute_qc_invalid_bin():
    """test if invalid bin size is handled correctly"""
    with pytest.raises(ValueError):
        qp.compute_qc_metrics(sdata_test(), bin_size=5)

def test_plot_qc_missing_metric():
    """test if missing metric is handled correctly with correct error message"""
    sdata = sdata_test()  # no metric available
    with pytest.raises(ValueError, match="Metric 'total_counts' not found"):
        qp.plot_qc_metrics(sdata, id="abcd", metric="total_counts")