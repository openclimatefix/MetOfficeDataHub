""" Main Application on top of wrapper

This gives an easy way to download all files from an order
"""
import logging
import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import uuid4

import cfgrib
import fsspec
import numcodecs
import pandas as pd
import psutil
import s3fs
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


def make_output_filenames(
    dataset: xr.Dataset, save_dir: str, output_type: str = "netcdf"
) -> List[str]:
    """
    Make two filenames to be saved

    # 1. use the date timestamp of the data. Idea is that this will keep the historic
    # 2. the latest - shows the most recent data without search through historic.

    :param dataset: The Xarray Dataset to be save
    :param save_dir: the directory where data is saved.
        The zarr file will be saved using the timestamp of the run in isoformat
    :param output_type: what file type should it be saved as.
        The options 'are netcdf' or 'zarr'
    """

    logger.debug("Making file names for saving data")
    assert output_type in ["zarr", "netcdf"]

    # get time of predictions
    time = pd.to_datetime(dataset.init_time.values)

    # if there are multiple times, just select the first one
    if type(time) == pd.DatetimeIndex:
        time = time[0]

    # make file names
    filename = time.tz_localize("UTC").isoformat()
    filename_and_path = f"{save_dir}/{filename}.{output_type}"
    filename_and_path_latest = f"{save_dir}/latest.{output_type}"

    # extra step needed if we are saving to AWS.
    # There may be different steps if saving to different file systems
    if fsspec.open(save_dir).fs == s3fs.S3FileSystem() and output_type == "zarr":
        filename_and_path = fsspec.get_mapper(
            filename_and_path, client_kwargs={"region_name": "eu-west-1"}
        )
        filename_and_path_latest = fsspec.get_mapper(
            filename_and_path_latest, client_kwargs={"region_name": "eu-west-1"}
        )

    return [filename_and_path, filename_and_path_latest]


def save(dataset: xr.Dataset, save_dir: str, save_latest: bool = True, output_type: str = "netcdf"):
    """
    Save dataset to zarr file

    :param dataset: The Xarray Dataset to be save
    :param save_dir: the directory where data is saved.
        The zarr file will be saved using the timestamp of the run in isoformat
    :param save_latest: option to save as 'latest.netcdf'
    :param output_type: what file type should it be saved as.
        The options 'are netcdf' or 'zarr'
    """

    logger.info(f"Saving data to {output_type} file here: {save_dir}")

    assert output_type in ["zarr", "netcdf"]

    # Make two files names
    # 1. use the date timestamp of the data. Idea is that this will keep the historic
    # 2. the latest - shows the most recent data without search through historic.
    filename_and_path, filename_and_path_latest = make_output_filenames(
        dataset=dataset, save_dir=save_dir, output_type=output_type
    )

    # option to save latest or not
    if save_latest:
        logger.debug(f"Saving latest file {filename_and_path_latest}")
        save_to_s3(
            dataset=dataset, filename_and_path=filename_and_path_latest, output_type=output_type
        )

    # save historic data
    logger.debug(f"Saving file {filename_and_path}")
    save_to_s3(dataset=dataset, filename_and_path=filename_and_path, output_type=output_type)


def save_to_s3(dataset: xr.Dataset, filename_and_path: str, output_type):
    """Save to s3"""

    if output_type == "zarr":
        # encoding used when saving to zarr file
        encoding = {
            var: {"compressor": numcodecs.Blosc(cname="zstd", clevel=5)}
            for var in dataset.data_vars
        }

        dataset.to_zarr(store=filename_and_path, mode="w", encoding=encoding, consolidated=True)
    else:
        save_to_netcdf_to_s3(dataset=dataset, filename=filename_and_path)


def save_to_netcdf_to_s3(dataset: xr.Dataset, filename: str):
    """Save xarray to netcdf in s3

    1. Save in temp local dir
    2. upload to s3 to temp name
    3. remove file and then rename

    :param dataset: The Xarray Dataset to be save
    :param filename: The s3 filname
    """
    with tempfile.TemporaryDirectory() as dir:
        # 1. save locally
        path = f"{dir}/temp.netcdf"
        dataset.to_netcdf(path=path, mode="w", engine="h5netcdf")

        # 2. save to s3
        filename_temp = str(Pathy.fluid(filename).parent.joinpath(str(uuid4()) + ".netcdf"))
        filesystem = fsspec.open(filename_temp).fs
        filesystem.put(path, filename_temp)

        # 3. remove and rename over
        filesystem.mv(filename_temp, filename)
