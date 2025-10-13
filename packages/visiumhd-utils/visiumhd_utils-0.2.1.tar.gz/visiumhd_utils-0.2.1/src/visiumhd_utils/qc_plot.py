"""
qc_plot.py
Functions to plot preliminary QC plots. Pre-processing using read_data functions is required
"""
import matplotlib.pyplot as plt
import spatialdata_plot # used for rendering images method
import numpy as np
import scanpy as sc

def compute_qc_metrics(sdata, bin_size = 2, mito_prefix="MT-"):
    """
    Compute standard QC metrics using Scanpy and add log-transformed total counts.
    Coupled with plot_qc_metrics below
    Reference: https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.calculate_qc_metrics.html

    Adds the following columns to sdata.tables["square_002um"].obs:
    - 'total_counts': sum of raw counts per spot
    - 'n_genes_by_counts': number of genes per spot
    - 'pct_counts_mt': percent of counts from mito genes
    - 'log_total_counts': log1p of total counts

    Args:
    sdata: the SpatialData 
    bin_size: bin resolution in um (must be from 2,8,16). default to 2um
    mito_prefix: prefix used to identify mitochondrial genes (default is "MT-")

    Return:
    Modified SpatialData object with updated QC metrics.
    """
    if bin_size not in [2, 8, 16]:
        raise ValueError("bin_size must be one of: 2, 8, 16") # double check bin size
    bin_str = f"{bin_size:03d}um" # padding
    table_key = f"square_{bin_str}"
    adata = sdata.tables[table_key]
    # Add boolean column (to identify MT genes) to var
    adata.var["mt"] = adata.var_names.str.startswith(mito_prefix)

    # Calculate QC metrics using scanpy
    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars={"mt": adata.var["mt"]},
        percent_top=None,
        log1p=False,
        inplace=True
    )

    # Add log-transformed total counts
    adata.obs["log_total_counts"] = np.log1p(adata.obs["total_counts"].values)

    return sdata


def plot_qc_metrics(sdata, id, metric, bin_size=2, cmap="viridis", vmin=None, vmax=None, save_path=None, figsize=(10, 10)):
    """
    Plot a single QC metric (e.g., total counts, % mito) at 2um resolution.

    Args:
    sdata: the SpatialData object
    id: ID of the VisiumHD dataset (ex. "H1-TRH234F_D1")
    metric: name of the QC metric in sdata.tables["square_002um"].obs to visualize.
            Examples: "total_counts", "log_total_counts", "n_genes_by_counts", "pct_counts_mt" from compute function
    bin_size: bin resolution in um (must be from 2,8,16). default to 2um
    cmap: matplotlib colormap name (default: "viridis")
    vmin: (optional) lower limit for color scale
    vmax: (optional) upper limit for color scale
    save_path: (optional) the path to save figure. If None (default), shows plot interactively.
    figsize: tuple, optional. Figure size in inches (default: (10, 10))
    """
    from spatialdata_plot.pl.utils import set_zero_in_cmap_to_transparent

    if bin_size not in [2, 8, 16]:
        raise ValueError("bin_size must be one of: 2, 8, 16")

    bin_str = f"{bin_size:03d}um"
    table_key = f"square_{bin_str}"
    bin_key = f"{id}_{table_key}"
    adata = sdata.tables[table_key]

    # Validate metric exists
    if metric not in adata.obs.columns:
        raise ValueError(f"Metric '{metric}' not found in sdata.tables['{table_key}'].obs")

    # Make zero-transparent colormap for sparse data
    custom_cmap = set_zero_in_cmap_to_transparent(cmap=cmap)

    # plot
    sdata.pl.render_shapes(
        bin_key,
        color=metric,
        cmap=custom_cmap,
        vmin=vmin,
        vmax=vmax,
        method = "datashader",
        datashader_reduction = "max" # to preserve max of the data for colorscale
    ).pl.show(
        coordinate_systems="global",
        title=f"{bin_size}um QC: {metric}",
        figsize=figsize,
        save=save_path
    )

def plot_gene_exp(sdata, id, gene_name, figsize=(10,10)):
    """
    Plots gene expression of a particular gene across 16um and 8um bins
    If no expression in a particular bin, the bin is transparent
    Otherwise, follows the scale in the generated figure

    Args:
    sdata: the SpatialData object
    id: the ID of the VisiumHD dataset, ex: 'H1-TRH234F_D1'
    gene_name: the gene of interest
    """
    # make the color scale
    # sparsity - visualize non-zero entries only, use FULL-RES image as background
    from spatialdata_plot.pl.utils import set_zero_in_cmap_to_transparent
    # display the areas where no expression is detected as transparent
    new_cmap = set_zero_in_cmap_to_transparent(cmap="viridis")

    for bin_size in [16, 8]:
        sdata.pl.render_shapes(
            f"{id}_square_{bin_size:03}um",
            color=gene_name,
            cmap=new_cmap
        ).pl.show(
            coordinate_systems="global",
            title=f"bin_size={bin_size}µm",
            figsize=figsize
        )


def plot_full_image(sdata, image_key):
    """
    Plots the full image for reference.

    Args:
    sdata: the SpatialData object
    image_key: the key to the image plotted. Ex: "H1-TRH234F_D1_full_image"
    """
    fig, ax = plt.subplots(figsize=(5, 5))  # Single plot   
    # Plot the full resolution image
    sdata.pl.render_images(image_key).pl.show(ax=ax, title="Full Image")
    plt.tight_layout()
    plt.show()


def plot_cropped_image(sdata, xmin, ymin, xmax, ymax, image_key):
    """
    Plot a cropped region of the image.

    Args:
    sdata: the SpatialData object
    xmin: the min x coordinate
    ymin: the min y coordinate
    xmax: the max x coordinate
    ymax: the max y coordinate
    image_key: the key to the image plotted. Ex: "H1-TRH234F_D1_full_image"
    """
    from spatialdata import bounding_box_query
    fig, ax = plt.subplots(figsize=(5, 5))  # Single plot

    # Define crop function
    crop0 = lambda x: bounding_box_query(
        x, 
        min_coordinate=[xmin, ymin], 
        max_coordinate=[xmax, ymax], 
        axes=("x", "y"), 
        target_coordinate_system="global"
    )

    sdata_cropped = crop0(sdata)

    # Apply crop and plot only the full image
    sdata_cropped.pl.render_images(image_key).pl.show( # type: ignore
        ax=ax, 
        title="Full Image (Cropped)", 
        coordinate_systems="global"
    )
    plt.tight_layout()
    plt.show()