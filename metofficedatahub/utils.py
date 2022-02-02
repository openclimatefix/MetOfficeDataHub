""" Utils functions """
import logging

import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)

DY_METERS = DX_METERS = 2_000

# TODO
# Got these from https://gridded-data-ui.cda.api.metoffice.gov.uk/select-region
NORTH = 1262937.2520015072 - 4000
SOUTH = -22383.68950705031 + 4000
EAST = 704564.7522423521 - 4000
WEST = -212346.9701878212 + 4000

NORTHING = np.arange(start=SOUTH, stop=NORTH, step=DY_METERS, dtype=np.int32)
EASTING = np.arange(start=WEST, stop=EAST, step=DX_METERS, dtype=np.int32)
NUM_ROWS = len(NORTHING)
NUM_COLS = len(EASTING)


def add_x_y(dataset: xr.Dataset) -> xr.Dataset:
    """Add x and y coordinates

    This is specifically for the UK model,
    see above where these values are made.
    """

    return dataset.assign_coords(
        {
            "x": ("x", EASTING),
            "y": ("y", NORTHING),
        }
    )


def post_process_dataset(dataset: xr.Dataset) -> xr.Dataset:
    """Get the Dataset ready for saving to Zarr.

    Convert the Dataset (with differet DataArrays for each NWP variable)
    to a single DataArray with a `variable` dimension.  We do this so each
    Zarr chunk can hold multiple NWP variables (which is useful because
    we often load all the NWP variables at once).

    Rename `time` to `init_time` (because `time` is ambiguous.  NWPs have two "times":
    the initialisation time and the target time).

    Rechunk the Dataset.  Rechunking at this step (instead of specifying chunks using the
    `dataset.to_zarr(encoding=...)`) has two advantages:  1) We can name the dimensions; and
    2) Chunking at this stage converts the Dataset into a Dask dataset, which adds a second
    level of parallelism.
    """
    logger.debug("Post-processing dataset...")
    da = dataset.to_array(dim="variable", name="UKV")

    # Reverse `lattitude` so it's top-to-bottom (so ZarrDataSource.get_example() works correctly!)
    # Adapted from:
    # https://stackoverflow.com/questions/54677161/xarray-reverse-an-array-along-one-coordinate
    y_reversed = da.y[::-1]
    da = da.reindex(y=y_reversed)

    return (
        da.to_dataset()
        .rename({"time": "init_time"})
        .chunk(
            {
                "init_time": 1,
                "step": 1,
                "y": len(dataset.y) // 2,
                "x": len(dataset.x) // 2,
                "variable": -1,
            }
        )
    )
