"""
read_data.py
This file defines functions to read in VisiumHD data and convert to appropriate forms for analyses.
"""
from spatialdata_io import visium_hd
import spatialdata as sd
import shutil
import os
import copy

def to_spatialdata(raw_folder_path, id, fullres_image_path = 'outs/spatial/tissue_hires_image.png'):
    """
    This function reads in a raw Visium HD dataset, write to Zarr format
    then read in the Zarr data, and convert to a SpatialData object.
    (the Zarr directory is temporarily generated and then removed before returning)
    CAREFUL: WRITE access is needed to the original VisiumHD folder because of spatialdata limitation

    Args: 
    raw_folder_path: the path to the raw Visium HD data folder (outermost)
    id: the ID of the VisiumHD dataset, ex: 'H1-TRH234F_D1'
    fullres_image_path: the relative path to the tissue_hires_image in VisiumHD output. default to the one in outs folder

    Return:
    sdata, the resulting SpatialData object for downstream processing
    """
    # create a temporary address for the zarr file
    zarr_path = "temp.zarr" 
    # spatialdata library limitation: feature_slice.h5 needs to appear in the outermost directory
    # with its name changed to id_feature_slice.h5 (ex: H1-TRH234F_D1_feature_slice.h5)
    # copy feature_slice.h5 in the outs/ folder to the raw_folder_path, and rename to id_feature_slice.h5 where id the passed in param
    dst_feature_slice = os.path.join(raw_folder_path, f"{id}_feature_slice.h5")
    src_feature_slice = os.path.join(raw_folder_path, "outs", "feature_slice.h5")
    shutil.copyfile(src_feature_slice, dst_feature_slice)

    # read HD data, write/read from Zarr
    sdata = visium_hd(raw_folder_path, dataset_id = id, fullres_image_file = fullres_image_path)
    sdata.write(zarr_path)
    sdata = sd.read_zarr(zarr_path)
    sdata = copy.deepcopy(sdata) # deep copy to detach from Zarr
    sdata.path = None # reset Zarr path to avoid issues
    # summary
    print(sdata)
    # make the var names unique
    for table in sdata.tables.values():
        table.var_names_make_unique()
    # cleanup
    shutil.rmtree(zarr_path)
    os.remove(dst_feature_slice)
    return sdata