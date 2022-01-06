from metofficeamd.app import MetOfficeAMD
from unittest import mock
from tests.conftest import (
    mock_get_order_list,
    mock_get_orders_details,
    mock_get_file_details,
    mock_get_example_grib,
)
import tempfile


def test_init():
    _ = MetOfficeAMD(client_id="fake", client_secret="fake")


@mock.patch("requests.get")
def test_get_orders(mock_get):
    mock_get.return_value = mock_get_order_list()

    amd = MetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_orders()


@mock.patch("requests.get")
def test_latest_order(mock_get):
    mock_get.return_value = mock_get_orders_details()

    order_id = "test_order_id"

    amd = MetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_lastest_order(order_id=order_id)


@mock.patch("requests.get")
def test_latest_order_file_id(mock_get):
    mock_get.return_value = mock_get_file_details()

    order_id = "test_order_id"
    file_id = "atmosphere_high-cloud-cover+low-cloud-cover+medium-cloud-cover_+06_0"

    amd = MetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_lastest_order_file_id(order_id=order_id, file_id=file_id)


@mock.patch("requests.get")
def test_latest_order_file_id_data(mock_get):
    mock_get.return_value = mock_get_example_grib()
    order_id = "test_order_id"
    file_id = "atmosphere_high-cloud-cover+low-cloud-cover+medium-cloud-cover_+06_0"

    with tempfile.TemporaryDirectory() as tmpdirname:
        amd = MetOfficeAMD(cache_dir=tmpdirname, client_id="fake", client_secret="fake")
        amd.get_lastest_order_file_id_data(order_id=order_id, file_id=file_id)
