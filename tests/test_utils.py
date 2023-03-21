import xarray as xr
import numpy as np

from metofficedatahub.utils import post_process_dataset


def test_post_process_dataset():
    seq_length = 10
    channels = 2
    image_size_pixels_width = 5
    image_size_pixels_height = 5
    init_times = 2

    dims = ("time", "step", "variables", "y", "x")
    new_dims = ("init_time", "step", "variables", "y", "x")

    image_data_array = xr.DataArray(
        data=abs(  # to make sure average is about 100
            np.random.uniform(
                0,
                200,
                size=(
                    init_times,
                    seq_length,
                    channels,
                    image_size_pixels_height,
                    image_size_pixels_width,
                ),
            )
        ),
        dims=dims,
        # coords=coords,
        name="data",
    )  # Fake data for testing!

    image_dataset = image_data_array.to_dataset(name="UKV")

    da = post_process_dataset(dataset=image_dataset)

    for d in new_dims:
        assert d in da.dims
