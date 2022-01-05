from metofficeamd.app import MetOfficeAMD
from unittest import mock
from tests.conftest import mock_get_run_list, mock_get_run_list_for_model
import tempfile



@mock.patch('requests.get')
def test_get_runs(mock_get):
    mock_get.return_value = mock_get_run_list()
    
    amd = MetOfficeAMD()
    amd.get_runs()


@mock.patch('requests.get')
def test_get_runs_model_id(mock_get):
    mock_get.return_value = mock_get_run_list_for_model()
    
    model_id = "mo-uk"

    amd = MetOfficeAMD()
    amd.get_runs_model_id(model_id=model_id)
