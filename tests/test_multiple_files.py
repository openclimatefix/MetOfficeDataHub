import os
import tempfile
from unittest import mock

import xarray as xr

from metofficedatahub.multiple_files import save_to_zarr
from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_download_all_none(mock_get, metofficedatahub):
    """Check that if there are no order ids, then no data is downloaded"""
    metofficedatahub.download_all_files(order_ids=[])

    assert len(metofficedatahub.files) == 0



@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_download_all(mock_get, metofficedatahub):
    """Check that if there are order ids, then  data is downloaded"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        metofficedatahub.cache_dir = tmpdirname
        metofficedatahub.download_all_files(order_ids=["test_order_id"])

        assert len(metofficedatahub.files) > 0
        for file in metofficedatahub.files:
            assert os.path.exists(file.local_filename)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_load_all_files(mock_get, metofficedatahub):

    metofficedatahub.download_all_files(order_ids=["test_order_id"])
    data = metofficedatahub.load_all_files()
    assert type(data) == xr.Dataset
    assert len(data.data_vars) > 0


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_save_to_zarr(mock_get, metofficedatahub):

    metofficedatahub.download_all_files(order_ids=["test_order_id"])
    data = metofficedatahub.load_all_files()

    with tempfile.TemporaryDirectory() as tmpdirname:
        save_to_zarr(data, save_dir=tmpdirname)

        assert os.path.exists(f'{tmpdirname}/latest.zarr')
