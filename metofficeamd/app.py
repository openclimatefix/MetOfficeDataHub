import logging
from typing import List, Optional

import cfgrib
import xarray as xr

from metofficeamd.base import BaseMetOfficeAMD

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


class MetOfficeAMD(BaseMetOfficeAMD):
    """Class built on top of BaseMetOfficeAMD used for processing multiple files"""

    def download_all_files(self, order_ids: Optional[List[str]] = None):
        """Download all files in the latest"""

        if order_ids is None:
            all_orders = self.get_orders()
            order_ids = [order.orderId for order in all_orders.orders]

        # loop over orders
        self.files = []
        for order_id in order_ids:

            logger.debug(f"Loading files from order {order_id}")

            self.order_details = self.get_lastest_order(order_id=order_id)

            # loop over all files
            for file in self.order_details.files:
                file_id = file.fileId

                variable = file.fileId
                datetime = variable.split("_")[-2]

                # There seems to be two files that are the same, one with '+HH' and one with 'YYYYMMDDHH'
                if datetime[0] != "+":

                    # download file
                    filename = self.get_lastest_order_file_id_data(
                        order_id=order_id, file_id=file_id
                    )

                    # put local file in file object
                    file.local_filename = filename
                    self.files.append(file)

    def load_file(self, file) -> xr.Dataset:
        """Load one grib file"""

        datasets_from_grib: list[xr.Dataset] = cfgrib.open_datasets(file)

        merged_ds = xr.merge(datasets_from_grib)

        return merged_ds

    def load_all_files(self) -> xr.Dataset:
        """Load all files and join them together"""

        # loop over all files and load them
        all_datasets_per_filename = {}
        for file in self.files:
            variable = file.fileId
            variable = variable.split("_")[1]

            dataset = self.load_file(file=file.local_filename)
            if variable not in all_datasets_per_filename.keys():
                all_datasets_per_filename[variable] = [dataset]
            else:
                all_datasets_per_filename[variable].append(dataset)

        # loop over different variables and join them together
        all_dataset = []
        for k, v in all_datasets_per_filename.items():

            # join all variables toegther
            dataset = xr.concat(v, dim="step")

            # remove un-needed variables
            for var in VARS_TO_DELETE:
                if var in dataset.variables:
                    del dataset[var]

            all_dataset.append(dataset)

        dataset = xr.merge(all_dataset)

        return dataset
