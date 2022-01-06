import tempfile
from unittest import mock

from metofficeamd.base import BaseMetOfficeAMD
from tests.conftest import mocked_requests_get


def test_init():
    _ = BaseMetOfficeAMD(client_id="fake", client_secret="fake")


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_orders(mock_get):

    amd = BaseMetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_orders()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order(mock_get):

    order_id = "test_order_id"

    amd = BaseMetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_lastest_order(order_id=order_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id(mock_get):

    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    amd = BaseMetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_latest_order_file_id(order_id=order_id, file_id=file_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id_data(mock_get):

    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    with tempfile.TemporaryDirectory() as tmpdirname:
        amd = BaseMetOfficeAMD(cache_dir=tmpdirname, client_id="fake", client_secret="fake")
        amd.get_lastest_order_file_id_data(order_id=order_id, file_id=file_id)
