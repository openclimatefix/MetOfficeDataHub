from unittest import mock

from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs(mock_get, basemetofficedatahub):
    basemetofficedatahub.get_runs()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs_model_id(mock_get, basemetofficedatahub):
    basemetofficedatahub.get_runs_model_id(model_id="mo-uk")
