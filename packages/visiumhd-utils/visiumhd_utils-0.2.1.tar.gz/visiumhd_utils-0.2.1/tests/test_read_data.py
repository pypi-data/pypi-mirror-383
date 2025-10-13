"""
The read_data.to_spatialdata() helper is essentially a wrapper of spatialdata-io,
as well as some additional manipulations on file structures with respect to real HD data. 
Currently, we do not have a lightweight public Visium HD dataset to implement the tests.
Will revisit later if necessary.
"""
import pytest
pytest.skip(
    "Skipping read_data tests: wrapper depends on real Visium HD input",
    allow_module_level=True,
)