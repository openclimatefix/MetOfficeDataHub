""" Utils functions """
import logging
import os

import numpy as np
import psutil
import pyproj
import xarray as xr
from scipy.interpolate import griddata

# OSGB is also called "OSGB 1936 / British National Grid -- United
# Kingdom Ordnance Survey".  OSGB is used in many UK electricity
# system maps, and is used by the UK Met Office UKV model.  OSGB is a
# Transverse Mercator projection, using 'easting' and 'northing'
# coordinates which are in meters.  See https://epsg.io/27700
OSGB = 27700

# WGS84 is short for "World Geodetic System 1984", used in GPS. Uses
# latitude and longitude.
WGS84 = 4326
WGS84_CRS = f"EPSG:{WGS84}"

logger = logging.getLogger(__name__)

DY_METERS = DX_METERS = 2_000

# The data seems to not be exactly on a OSGB grid, therefore we are going to reproject the data
# TODO (investigate why this is)
# Got these from https://gridded-data-ui.cda.api.metoffice.gov.uk/select-region
NORTH = 1262937.2520015072 - 10000
SOUTH = -22383.68950705031 + 10000
EAST = 704564.7522423521 - 10000
WEST = -212346.9701878212 + 10000
# they adjusted by 10,000 so that there are no nans when the data is reprojected to a grid

NORTHING = np.arange(start=SOUTH, stop=NORTH, step=DY_METERS, dtype=np.int32)
EASTING = np.arange(start=WEST, stop=EAST, step=DX_METERS, dtype=np.int32)
NUM_ROWS = len(NORTHING)
NUM_COLS = len(EASTING)


def add_x_y(dataset: xr.Dataset) -> xr.Dataset:
    """Add x and y coordinates

    This is specifically for the UK model,
    see above where these values are made.
    """

    # transform to osgb
    lat_lon_to_osgb = pyproj.Transformer.from_crs(crs_from=WGS84, crs_to=OSGB)
    x, y = lat_lon_to_osgb.transform(dataset.latitude, dataset.longitude)

    # new grid
    x_grid, y_grid = np.meshgrid(EASTING, NORTHING)
    points = np.array([y.ravel(), x.ravel()])
    points = points.transpose().tolist()

    # # interpolate lat lon, could take about 6 seconds
    logger.debug("Resampling lat and lon values")
    lat = griddata(
        points=points, values=dataset.latitude.values.ravel(), xi=(y_grid, x_grid), method="linear"
    )
    lon = griddata(
        points=points, values=dataset.longitude.values.ravel(), xi=(y_grid, x_grid), method="linear"
    )
    process = psutil.Process(os.getpid())
    logger.debug(f"Memory is {process.memory_info().rss / 10 ** 6} MB")

    data_vars = list(dataset.data_vars)
    data_vars_all = {}
    for data_var in data_vars:
        logger.debug(f"Resampling {data_var}")

        data = dataset.__getitem__(data_var)
        dataset.drop_vars(data_var)

        n1, n2, ny, nx = data.shape
        data_gird = np.zeros((n1, n2, NUM_ROWS, NUM_COLS))

        # need to loop of 'init_time' and 'step'
        for i in range(n1):
            for j in range(n2):
                values = data[i, j].values.ravel()
                # The following different methods can be used.
                # nearest - 0.4 seconds
                # linear - 2.9 seconds
                # cubic - 3.3 seconds
                # The timings are for a (639, 455) image
                tt = griddata(points=points, values=values, xi=(y_grid, x_grid), method="nearest")
                data_gird[i, j] = tt

        process = psutil.Process(os.getpid())
        logger.debug(f"Memory is {process.memory_info().rss / 10 ** 6} MB")

        data_vars_all[data_var] = xr.DataArray(
            **{"dims": ["time", "step", "y", "x"], "data": data_gird, "attrs": data.attrs}
        )

    # create new dataset
    new_dataset = xr.Dataset(
        data_vars=data_vars_all,
        coords={
            "time": dataset.time,
            "step": dataset.step,
            "y": ("y", NORTHING),
            "x": ("x", EASTING),
            "latitude": (["y", "x"], lat, dataset.latitude.attrs),
            "longitude": (["y", "x"], lon, dataset.longitude.attrs),
        },
        attrs=dataset.attrs,
    )

    return new_dataset


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
    
    process = psutil.Process(os.getpid())
    logger.debug(f"Memory is {process.memory_info().rss / 10 ** 6} MB")

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
