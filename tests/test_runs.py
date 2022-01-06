import tempfile
from unittest import mock

from metofficeamd.base import BaseMetOfficeAMD
from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs(mock_get):

    amd = BaseMetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_runs()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs_model_id(mock_get):

    model_id = "mo-uk"

    amd = BaseMetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_runs_model_id(model_id=model_id)
