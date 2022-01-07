import tempfile
from unittest import mock

from metofficedatahub.base import BaseMetOfficeDataHub
from tests.conftest import mocked_requests_get


def test_init():
    _ = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_orders(mock_get):

    datahub = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")
    datahub.get_orders()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order(mock_get):

    order_id = "test_order_id"

    datahub = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")
    datahub.get_lastest_order(order_id=order_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id(mock_get):

    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    datahub = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")
    datahub.get_latest_order_file_id(order_id=order_id, file_id=file_id)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_latest_order_file_id_data(mock_get):

    order_id = "test_order_id"
    file_id = "agl_temperature_00"

    with tempfile.TemporaryDirectory() as tmpdirname:
        datahub = BaseMetOfficeDataHub(cache_dir=tmpdirname, client_id="fake", client_secret="fake")
        datahub.get_lastest_order_file_id_data(order_id=order_id, file_id=file_id)
