""" Main Application on top of wrapper

This gives an easy way to download all files from an order
"""
import logging
import math
import os
from datetime import datetime, timedelta, timezone
from typing import List

import cfgrib
import fsspec
import pandas as pd
import psutil
import xarray as xr
from pathy import Pathy

from metofficedatahub.base import BaseMetOfficeDataHub
from metofficedatahub.utils import add_x_y, post_process_dataset

logger = logging.getLogger(__name__)

VARS_TO_DELETE = (
    "unknown",
    "valid_time",
    "heightAboveGround",
    "heightAboveGroundLayer",
    "atmosphere",
    "cloudBase",
    "surface",
    "meanSea",
    "level",
)

variable_name_translation = {
    "temperature": {"t2m": "t"},
    "wind-speed-surface-adjusted": {"unknown": "si10"},
    "rain-precipitation-rate": {"rprate": "prate"},
}

HOUR_IN_PAST = 7


class MetOfficeDataHub(BaseMetOfficeDataHub):
    """Class built on top of BaseMetOfficeDataHub used for processing multiple files"""

    folder_to_download = "./temp"

    if ~os.path.exists(folder_to_download):
        try:
            os.mkdir(folder_to_download)
        except Exception as e:
            logger.debug(f"Could not make folder {folder_to_download} - {e}")

    def download_all_files(self, order_ids: List[str]):
        """Download all latest files for specified orders.

        If no orders are specified, nothing is downloaded.
        """

        # loop over orders
        self.files = []
        for order_id in order_ids:
            logger.debug(f"Loading files from order {order_id}")

            self.order_details = self.get_lastest_order(order_id=order_id)

            logger.debug(f"There are {len(self.order_details.files)} files to load")

            # loop over all files
            for i, file in enumerate(self.order_details.files):
                logger.debug(f"Downloading file {i} out of {len(self.order_details.files)}")

                file_id = file.fileId

                variable = file.fileId
                datetime = variable.split("_")[-1]
                logger.debug(f"Date time of file is {datetime}")

                # There seem to be two files that are the same,
                # one with '+HH' and one with 'YYYYMMDDHH'
                if datetime[0] != "+":
                    # download file
                    filename = self.get_latest_order_file_id_data(
                        order_id=order_id, file_id=file_id
                    )

                    # put local file in file object
                    file.local_filename = filename
                    self.files.append(file)
                else:
                    logger.debug(f"Not adding {file_id} to list")

        logger.info(f"All files downloaded ({len(self.files)}")

    def load_file(self, file) -> xr.Dataset:
        """Load one grib file"""

        logger.debug(f"Loading {file}")

        # make tempfilename
        filename = file.split("/")[-1]
        temp_filename = f"{self.folder_to_download}/{filename}"

        # save from s3 to local temp
        if ~os.path.exists(Pathy(temp_filename)):
            logger.debug(f"Moving {file} to {temp_filename}")
            fs = fsspec.open(Pathy.fluid(file).parent).fs
            fs.get(file, temp_filename)
        else:
            logger.debug(f"Already in local file, {temp_filename}")

        # load
        datasets_from_grib: list[xr.Dataset] = cfgrib.open_datasets(temp_filename)

        # merge
        merged_ds = xr.merge(datasets_from_grib)

        del datasets_from_grib

        return merged_ds

    def load_all_files(self) -> xr.Dataset:
        """Load all files and join them together"""

        logger.info("Now loading all files and joining them together")

        # loop over all files and load them
        all_datasets_per_filename = {}
        for i, file in enumerate(self.files):
            logger.debug(f"Loading file {i} out of {len(self.files)}")

            variable = file.fileId
            variable = variable.split("_")[1]

            dataset = self.load_file(file=file.local_filename)

            # filter time
            filter_time = datetime.now(timezone.utc) - timedelta(hours=HOUR_IN_PAST)

            # rename variables
            if variable in variable_name_translation:
                rename = variable_name_translation[variable]
                for key in rename.keys():
                    if key in dataset.data_vars:
                        logger.debug(f"Renaming {rename}")
                        dataset = dataset.rename(variable_name_translation[variable])
                    else:
                        logger.debug(f"Key ({key}) not in data vars")

            # remove un-needed variables
            for var in VARS_TO_DELETE:
                if var in dataset.variables:
                    del dataset[var]

            time = pd.to_datetime(dataset.time.values)
            time = time.replace(tzinfo=timezone.utc)
            logger.debug(f"Data is for {time}, {filter_time=}")
            if time < filter_time:
                logger.debug(
                    f"Not including file as the data is < {filter_time}, {file.local_filename}"
                )
            else:
                if variable not in all_datasets_per_filename.keys():
                    all_datasets_per_filename[variable] = [dataset]
                else:
                    all_datasets_per_filename[variable].append(dataset)

                del dataset

        # loop over different variables and join them together
        logger.info("Joining the dataset together")
        all_dataset = []
        keys = list(all_datasets_per_filename.keys())
        for k in keys:
            logger.debug(f"Merging dataset {k} out of {len(keys)}")

            v = all_datasets_per_filename.pop(k)

            # print memoery
            process = psutil.Process(os.getpid())
            logger.debug(f"Memory is {process.memory_info().rss / 10 ** 6} MB")

            # add time as dimension
            v = [vv.expand_dims("time") for vv in v]

            # merge dataset
            dataset = xr.merge(v)

            # join all variables together
            all_dataset.append(dataset)

            # save memory
            del v

        dataset = xr.merge(all_dataset)
        logger.debug(f"Loaded all files, {dataset.data_vars}")
        logger.debug(f"{dataset.time=}")
        logger.debug(f"{dataset.step=}")

        dataset = add_x_y(dataset)
        dataset = post_process_dataset(dataset)

        return dataset


def _get_first_init_time_as_str(dataset: xr.Dataset) -> str:
    """Extract the first `init_time` from the dataset and iso-format it.

    This is used to create a filename for the dataset.
    """
    # get time of predictions
    time = pd.to_datetime(dataset.init_time.values)

    # if there are multiple times, just select the first one
    if type(time) == pd.DatetimeIndex:
        time = time[0]

    return time.tz_localize("UTC").isoformat()


def _chunk(dataset: xr.Dataset, *, ideal_chunk_size_mb: float) -> xr.Dataset:
    """Return a chunked dataset based on a custom chunking scheme.

    This chunking scheme (chunks of given size that always include all the `step` and `variables`)
    works well in practice when we get the data for the pv-sites models.

    :param dataset: The dataset to be chunked.
    :param ideal_chunk_size_mb: Size of the chunks in Mb.
    """
    num_step = dataset.dims["step"]
    num_variables = dataset.dims["variable"]

    num_float_in_mb = 1024 * 1024 * 8

    size = int(math.sqrt(ideal_chunk_size_mb * num_float_in_mb / num_step / num_variables))
    return dataset.chunk(dict(init_time=1, step=num_step, variable=num_variables, x=size, y=size))


def save(dataset: xr.Dataset, save_dir: str, *, ideal_chunk_size_mb=1):
    """
    Save dataset

    :param dataset: The Xarray Dataset to be saved
    :param save_dir: the directory where data is saved. This can either be a local path or a
        "s3://..." path. 3 files similar files are created:
            * One using the timestamp of the first `init_time` as the filename
            * latest.netcdf
            * latest.zarr
    :param ideal_chunk_size_mb: Ideal chunk size in Mb for the .zarr file.
    """
    logger.info(f'Saving data to "{save_dir}"')

    filename = _get_first_init_time_as_str(dataset)
    path = f"{save_dir}/{filename}.netcdf"
    logger.debug(f'Saving data to "{path}"')
    save_to_s3(dataset, path)

    # Also save it as "lastest.<ext>", both in zarr and netcdf format.
    # TODO Copying the file we just wrote in AWS directly would be faster.
    logger.debug(f'Saving data to "{path}"')
    path = f"{save_dir}/latest.netcdf"
    save_to_s3(dataset, path)

    chunked = _chunk(dataset, ideal_chunk_size_mb=ideal_chunk_size_mb)
    logger.debug(f'Saving data to "{path}"')
    path = f"{save_dir}/latest.zarr"
    save_to_s3(chunked, path)


def save_to_s3(dataset: xr.Dataset, path: str):
    """Save to s3"""
    if path.endswith(".zarr"):
        dataset.to_zarr(store=path, mode="w", consolidated=True)
    elif path.endswith(".netcdf"):
        # xarray doesn't support writing .netcdf files directly to S3 like for .zarr files.
        # Also note the "simplecache::" and see https://github.com/pydata/xarray/issues/4122
        with fsspec.open("simplecache::" + path, mode="wb") as f:
            dataset.to_netcdf(f)
    else:
        assert False, "unexpected extension"
