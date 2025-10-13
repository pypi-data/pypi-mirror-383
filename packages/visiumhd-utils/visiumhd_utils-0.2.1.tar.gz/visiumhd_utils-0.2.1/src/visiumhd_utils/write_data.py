"""
write_data.py
This file defines functions to write updated spatialdata objects back to the original raw VisiumHD output form.
Some libraries, like FICTURE, want the original output folder as the input.
"""
import os
import pandas as pd
from scipy.io import mmwrite
import gzip

def write_2um_filtered_counts(sdata, raw_folder_path, new_name = "matrix_destriped.mtx.gz", overwrite = False):
    """
    Function that writes the filtered/destriped 2um counts back to the original HD folder, with a new file name.
    This is primarily intended to run after the destriping command ONLY.
    NOTE: this assumes gene list and barcodes unmodified.

    Args:
    sdata: the updated spatialdata object
    raw_folder_path: the raw VisiumHD folder (outermost directory)
    new_name: the file name for the new matrix
    overwrite: if False, raise error if overwriting happens
    """
    adata = sdata.tables["square_002um"] # extract data
    # define folders and file paths
    matrix_dir = os.path.join(
        raw_folder_path,
        "outs/binned_outputs/square_002um/filtered_feature_bc_matrix"
    )
    barcodes_path = os.path.join(matrix_dir, "barcodes.tsv.gz")
    features_path = os.path.join(matrix_dir, "features.tsv.gz")
    new_matrix_path = os.path.join(matrix_dir, new_name)

    # Load and validate barcode/gene information
    old_barcodes = pd.read_csv(barcodes_path, sep="\t", header=None).iloc[:, 0]
    old_genes = pd.read_csv(features_path, sep="\t", header=None).iloc[:, 1]

    assert (adata.obs_names == old_barcodes.values).all(), "Barcodes do not match!"
    assert (adata.var_names == old_genes.values).all(), "Gene names do not match!"

    # overwrite check
    if os.path.exists(new_matrix_path) and not overwrite:
        raise FileExistsError(
            f"{new_matrix_path} already exists."
        )

    # Write matrix to new file
    # Support both gz-compressed and plain matrix files
    if new_matrix_path.endswith(".gz"):
        with gzip.open(new_matrix_path, "wb") as new_file:
            mmwrite(new_file, adata.X)
    else:
        mmwrite(new_matrix_path, adata.X)