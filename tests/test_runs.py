import tempfile
from unittest import mock

from metofficeamd.app import MetOfficeAMD
from tests.conftest import mock_get_run_list, mock_get_run_list_for_model


@mock.patch("requests.get")
def test_get_runs(mock_get):
    mock_get.return_value = mock_get_run_list()

    amd = MetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_runs()


@mock.patch("requests.get")
def test_get_runs_model_id(mock_get):
    mock_get.return_value = mock_get_run_list_for_model()

    model_id = "mo-uk"

    amd = MetOfficeAMD(client_id="fake", client_secret="fake")
    amd.get_runs_model_id(model_id=model_id)
