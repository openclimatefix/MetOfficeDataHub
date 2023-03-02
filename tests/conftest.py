"""Conftest

To run this tests local you may need to add
export PYTHONPATH=${PYTHONPATH}:/tests
"""

import json
import os

import pytest
import xarray as xr
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_Forecast

from metofficedatahub.base import BaseMetOfficeDataHub
from metofficedatahub.constants import DOMAIN, ROOT
from metofficedatahub.multiple_files import MetOfficeDataHub


@pytest.fixture
def db_connection(tmp_path):
    """Database connection"""
    url = os.getenv("DB_URL", f"sqlite:///{tmp_path}/test.db")

    connection = DatabaseConnection(url=url, base=Base_Forecast, echo=False)
    Base_Forecast.metadata.create_all(connection.engine)

    yield connection

    Base_Forecast.metadata.drop_all(connection.engine)


@pytest.fixture
def basemetofficedatahub():
    """Fixture of BaseMetOfficeDataHub"""
    return BaseMetOfficeDataHub(client_id="fake", client_secret="fake")


@pytest.fixture
def metofficedatahub():
    """Fixture of MetOfficeDataHub"""
    return MetOfficeDataHub(client_id="fake", client_secret="fake")


def mocked_requests_get(*args, **kwargs):
    """Mocked requests get"""

    class MockResponse:
        def __init__(self, data, status_code):
            self.json_data = data
            self.status_code = status_code
            self.content = data

        def json(self):
            return self.json_data

    if args[0] == f"https://{DOMAIN}/{ROOT}/orders?detail=MINIMAL":
        filename = "order_list.json"
    elif args[0] == f"https://{DOMAIN}/{ROOT}/orders/test_order_id/latest?detail=MINIMAL":
        filename = "order_details.json"
    elif (
        args[0]
        == f"https://{DOMAIN}/{ROOT}/orders/test_order_id/latest/agl_temperature_00?detail=MINIMAL"
    ):
        filename = "file_details.json"
    elif (
        args[0] == f"https://{DOMAIN}/{ROOT}/orders/test_order_id/latest/agl_temperature_00/data?"
        "detail=MINIMAL"
    ):
        filename = "test_00.grib"
    elif args[0] == f"https://{DOMAIN}/{ROOT}/runs?detail=MINIMAL":
        filename = "run_list.json"
    elif args[0] == f"https://{DOMAIN}/{ROOT}/runs/mo-uk?detail=MINIMAL":
        filename = "run_list_for_model.json"
    else:
        raise Exception(f"url string has not been mocked {args[0]}")

    folder = "tests/data"
    if ".json" in filename:
        with open(f"{folder}/{filename}") as json_file:
            data = json.load(json_file)
    else:
        with open(f"{folder}/{filename}", "rb") as file:
            data = file.read()

    return MockResponse(data, 200)


def mocked_requests_get_error():
    """Mock API so it always gives 404"""

    class MockResponse:
        def __init__(self, data, status_code):
            self.json_data = data
            self.status_code = status_code
            self.content = data

        def json(self):
            return self.json_data

        @property
        def text(self):
            return "Page does not exist"

    return MockResponse("Page does not exist", 404)


@pytest.fixture
def met_office_all_files():
    """Xarray dataset that looks like what is returned by metofficedatahub.load_all_files()

    This allows running some tests way faster.
    """
    return xr.open_dataset("tests/fixtures/met_all_files.netcdf")
