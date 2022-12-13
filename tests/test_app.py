import tempfile
from unittest import mock

import xarray as xr
from click.testing import CliRunner
from freezegun import freeze_time

from metofficedatahub.app import run
from tests.conftest import mocked_requests_get, mocked_requests_get_error

runner = CliRunner()


@freeze_time("2022-01-01")
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_save_to_zarr(mock_get, db_connection):
    with tempfile.TemporaryDirectory() as tmpdirname:
        response = runner.invoke(
            run,
            [
                "--api-key",
                "fake",
                "--api-secret",
                "fake",
                "--order-id",
                "test_order_id",
                "--save-dir",
                tmpdirname,
            ],
        )
        assert response.exit_code == 0


@freeze_time("2022-01-01")
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_no_order_ids(mock_get, db_connection):
    with tempfile.TemporaryDirectory() as tmpdirname:
        response = runner.invoke(
            run,
            [
                "--api-key",
                "fake",
                "--api-secret",
                "fake",
                "--save-dir",
                tmpdirname,
            ],
        )
        assert response.exit_code == 1


@freeze_time("2022-01-01")
@mock.patch("requests.get", side_effect=mocked_requests_get_error)
def test_error(mock_get, db_connection):
    with tempfile.TemporaryDirectory() as tmpdirname:
        response = runner.invoke(
            run, ["--api-key", "fake", "--api-secret", "fake", "--save-dir", tmpdirname]
        )
        assert response.exit_code == 1
