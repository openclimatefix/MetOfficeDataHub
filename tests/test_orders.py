import os
import tempfile
from unittest import mock

from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_orders(mock_get, basemetofficedatahub):
    basemetofficedatahub.get_orders()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order(mock_get, basemetofficedatahub):
    order_id = "test_order_id"

    basemetofficedatahub.get_lastest_order(order_id=order_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id(mock_get, basemetofficedatahub):
    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    basemetofficedatahub.get_latest_order_file_id(order_id=order_id, file_id=file_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id_data(mock_get, basemetofficedatahub):
    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    with tempfile.TemporaryDirectory() as tmpdirname:
        basemetofficedatahub.cache_dir = tmpdirname
        filename = basemetofficedatahub.get_latest_order_file_id_data(
            order_id=order_id, file_id=file_id
        )
        assert os.path.exists(filename)
