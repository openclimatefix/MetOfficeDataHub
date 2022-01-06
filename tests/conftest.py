import json

from metofficeamd.constants import DOMAIN, ROOT


def mocked_requests_get(*args, **kwargs):
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
        == f"https://{DOMAIN}/{ROOT}/orders/test_order_id/latest/atmosphere_high-cloud-cover+low-cloud-cover+medium-cloud-cover_+06_0?detail=MINIMAL"
    ):
        filename = "file_details.json"
    elif (
        args[0]
        == f"https://{DOMAIN}/{ROOT}/orders/test_order_id/latest/atmosphere_high-cloud-cover+low-cloud-cover+medium-cloud-cover_+06_0/data?detail=MINIMAL"
    ):
        filename = "example.grib"
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
        with open(f"{folder}/example.grib", "rb") as file:
            data = file.read()

    return MockResponse(data, 200)
