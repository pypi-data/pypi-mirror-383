.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/visiumhd_utils.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/visiumhd_utils
    .. image:: https://readthedocs.org/projects/visiumhd_utils/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://visiumhd_utils.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/visiumhd_utils/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/visiumhd_utils
    .. image:: https://img.shields.io/pypi/v/visiumhd_utils.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/visiumhd_utils/
    .. image:: https://img.shields.io/conda/vn/conda-forge/visiumhd_utils.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/visiumhd_utils
    .. image:: https://pepy.tech/badge/visiumhd_utils/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/visiumhd_utils
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/visiumhd_utils
    .. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
        :alt: Project generated with PyScaffold
        :target: https://pyscaffold.org/

==============
visiumhd_utils
==============


    Tools for pre-processing and visualizing Visium HD spatial transcriptomics data.


Features
--------
- Read in raw VisiumHD data and convert to SpatialData objects
- Quality control metric plotting and image plotting
- Destripe counts from raw 2um bins
- Write updated counts back to raw VisiumHD data format

Installation
------------

Install from PyPI:

.. code-block:: bash

    pip install visiumhd-utils

Usage
-----

.. code-block:: python

    import visiumhd_utils.read_data as rd 
    import visiumhd_utils.qc_plot as qp
    import visiumhd_utils.destripe as ds
    import visiumhd_utils.write_data as wd

    sdata = rd.to_spatialdata("path/to/data", "id")
    qp.compute_qc_metrics(sdata)
    qp.plot_qc_metrics(sdata, "id", metric="pct_counts_mt")
    ds.destripe_b2c(sdata)
    wd.write_2um_filtered_counts(sdata, "path/to/folder")


Project Status
--------------

This package is in early development. Use with caution; interfaces may change. 


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
