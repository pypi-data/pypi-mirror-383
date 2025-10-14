import pathlib
from typing import Tuple

import h5py

from ._assert import demo_assert


@demo_assert("HDF5 dataset {data_path} in {filename} with shape {expected_shape}")
def assert_hdf5_dataset_exists(
    filename: pathlib.Path,
    data_path: str,
    expected_shape: Tuple[int, ...],
) -> None:
    if not filename.exists():
        raise AssertionError(f"{str(filename)!r} does not exist")
    filename = str(filename)
    with h5py.File(filename, mode="r") as root:
        if data_path not in root:
            raise AssertionError(f"{data_path!r} not in {filename!r}")

        dset = root[data_path]
        if dset.shape != expected_shape:
            url = f"{filename!r}::{data_path}"
            raise AssertionError(
                f"Shape of {url!r} is {dset.shape} instead of {expected_shape}"
            )
