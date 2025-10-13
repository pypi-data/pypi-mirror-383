from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from scipy.io import mmread
from scipy.sparse import csr_matrix

import visiumhd_utils.write_data as wd

def test_write_2um_filtered_counts(tmp_path):
    """tests the write data function"""
    # setup minimum structure to mimic a Visium HD raw folder
    root = tmp_path / "HD"
    mdir = root / "outs/binned_outputs/square_002um/filtered_feature_bc_matrix"
    mdir.mkdir(parents=True)

    barcodes = ["BC0", "BC1"]
    genes = ["G0", "G1", "G2"]

    pd.Series(barcodes).to_csv(
        mdir / "barcodes.tsv.gz",
        sep="\t", header=False, index=False, compression="gzip"
    )
    # write two columns to features.csv
    pd.DataFrame({
        "id": [f"id{i}" for i in range(len(genes))],
        "name": genes
    }).to_csv(
        mdir / "features.tsv.gz",
        sep="\t", header=False, index=False, compression="gzip"
    )

    # make up a minimal spatialdata object
    X = csr_matrix(np.arange(len(barcodes) * len(genes)).reshape(len(barcodes), len(genes)))
    adata = SimpleNamespace(X=X, obs_names=np.array(barcodes), var_names=np.array(genes))
    sdata = SimpleNamespace(tables={"square_002um": adata})

    # run the function
    new_name = "matrix_destriped.mtx.gz"
    wd.write_2um_filtered_counts(sdata, raw_folder_path=root, new_name=new_name)

    out_path = mdir / new_name
    assert out_path.exists() # assert if path exists
    # check if array written is equivalent
    np.testing.assert_array_equal(mmread(out_path).toarray(), X.toarray()) # type: ignore

    # check overwriting functionality
    with pytest.raises(FileExistsError):
        wd.write_2um_filtered_counts(sdata, root, new_name=new_name, overwrite=False)

    # check for barcode mismatch
    sdata.tables["square_002um"].obs_names = np.array([b + "_x" for b in barcodes]) # modified
    with pytest.raises(AssertionError):
        wd.write_2um_filtered_counts(sdata, root, new_name="tmp.mtx.gz")