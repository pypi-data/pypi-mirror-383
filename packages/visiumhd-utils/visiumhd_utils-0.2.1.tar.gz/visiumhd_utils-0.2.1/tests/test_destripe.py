from types import SimpleNamespace
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import anndata as ad
import visiumhd_utils.destripe as ds
import pytest

def test_destripe_b2c():
    """test function for destripe_b2c"""
    # make up spatialdata object with 2um bin data represented by AnnData object
    barcodes = ["BC0", "BC1", "BC2", "BC3"]
    genes = ["G0", "G1"]
    X = csr_matrix([[10, 0],
                    [20, 0],
                    [30, 0],
                    [40, 0]]) # 4 bins with 2 genes

    obs = pd.DataFrame({
        "array_row": [0, 0, 1, 1],
        "array_col": [0, 1, 0, 1]
    }, index=barcodes)
    var = pd.DataFrame(index=genes) # create empty df with only gene names

    adata = ad.AnnData(X, obs=obs, var=var)
    sdata = SimpleNamespace(tables={"square_002um": adata})

    # run at 50% quantile for easy computation
    ds.destripe_b2c(sdata, quantile=0.5)

    adata_out = sdata.tables["square_002um"]

    # check if all expected columns are present
    assert {"destripe_factor", "n_counts_adjusted", "n_counts"} <= set(adata_out.obs.columns)

    # check if n counts is properly updated -- should equal row-sums of X after scaling
    np.testing.assert_allclose(
        adata_out.obs["n_counts"].values,
        np.array(adata_out.X.sum(axis=1)).flatten(),
    )

def test_destripe_missing_table_raises():
    """test if missing 2um table raises an error"""
    sdata_empty = SimpleNamespace(tables={})
    with pytest.raises(KeyError, match="square_002um"):
        ds.destripe_b2c(sdata_empty)