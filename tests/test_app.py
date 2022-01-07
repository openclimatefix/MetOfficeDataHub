import tempfile
from unittest import mock

import xarray as xr
from click.testing import CliRunner

from metofficedatahub.app import run
from tests.conftest import mocked_requests_get

runner = CliRunner()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_save_to_zarr(mock_get):

    with tempfile.TemporaryDirectory() as tmpdirname:
        response = runner.invoke(
            run, ["--api-key", "fake", "--api-secret", "fake", "--save-dir", tmpdirname]
        )
        assert response.exit_code == 0
