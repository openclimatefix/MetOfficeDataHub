import tempfile
from unittest import mock

from metofficedatahub.base import BaseMetOfficeDataHub
from tests.conftest import mocked_requests_get


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs(mock_get):

    datahub = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")
    datahub.get_runs()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_runs_model_id(mock_get):

    model_id = "mo-uk"

    datahub = BaseMetOfficeDataHub(client_id="fake", client_secret="fake")
    datahub.get_runs_model_id(model_id=model_id)
