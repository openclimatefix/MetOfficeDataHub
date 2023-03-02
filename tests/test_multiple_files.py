import os
import tempfile
from datetime import datetime
from unittest import mock

import xarray as xr
from freezegun import freeze_time

from metofficedatahub.multiple_files import save
from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_download_all_none(mock_get, metofficedatahub):
    """Check that if there are no order ids, then no data is downloaded"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        metofficedatahub.cache_dir = tmpdirname

        metofficedatahub.download_all_files(order_ids=[])

        assert len(metofficedatahub.files) == 0


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_download_all(mock_get, metofficedatahub):
    """Check that if there are order ids, then their data is downloaded"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        metofficedatahub.cache_dir = tmpdirname
        metofficedatahub.download_all_files(order_ids=["test_order_id"])

        assert len(metofficedatahub.files) > 0
        for file in metofficedatahub.files:
            assert os.path.exists(file.local_filename)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_download_repeat(mock_get, metofficedatahub):
    """Check that files are not downloaded again"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        metofficedatahub.cache_dir = tmpdirname
        metofficedatahub.download_all_files(order_ids=["test_order_id"])

        assert len(metofficedatahub.files) > 0
        for file in metofficedatahub.files:
            assert os.path.exists(file.local_filename)

        # downloaded for second time
        datetime_now = datetime.now()
        metofficedatahub.download_all_files(order_ids=["test_order_id"])

        # make sure the files arent downloaded again
        for file in metofficedatahub.files:
            assert os.path.exists(file.local_filename)
            creation_time = os.path.getmtime(file.local_filename)
            assert datetime.fromtimestamp(creation_time) < datetime_now


@freeze_time("2022-01-01")
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_load_all_files(mock_get, metofficedatahub):
    with tempfile.TemporaryDirectory() as tmpdirname:
        metofficedatahub.cache_dir = tmpdirname

        metofficedatahub.download_all_files(order_ids=["test_order_id"])
        data = metofficedatahub.load_all_files()
        assert type(data) == xr.Dataset
        assert len(data.data_vars) > 0


def test_save(met_office_all_files, tmp_path):
    # Our fixture is small using the default `ideal_chunk_size` would make only one chunk.
    save(met_office_all_files, save_dir=tmp_path, ideal_chunk_size_mb=1 / 1024)

    # Make sure the 2 latest files have been created.
    assert os.path.exists(f"{tmp_path}/latest.netcdf")
    zarr_path = f"{tmp_path}/latest.zarr"
    assert os.path.exists(zarr_path)

    # Verify the chunks of the zarr file.
    # In practice we don't need the `chunks="auto"` argument, but we need it for the chunks to
    # represent the files.
    ds = xr.open_dataset(zarr_path, chunks="auto", engine="zarr")
    assert ds.chunks == dict(variable=(1,), init_time=(1,), step=(13,), y=(10,), x=(10,))
