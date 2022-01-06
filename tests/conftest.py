import json

from requests import Response


def mock_get(filename):
    response = Response()

    folder = "tests/data"

    with open(f"{folder}/{filename}") as json_file:
        data = json.load(json_file)

    response._content = json.dumps(data).encode()
    response.status_code = 200

    return response


def mock_get_order_list():
    return mock_get("order_list.json")


def mock_get_orders_details():
    return mock_get("order_details.json")


def mock_get_file_details():
    return mock_get("file_details.json")


def mock_get_run_list():
    return mock_get("run_list.json")


def mock_get_run_list_for_model():
    return mock_get("run_list_for_model.json")


def mock_get_example_grib():
    response = Response()

    folder = "tests/data"

    with open(f"{folder}/example.grib", "rb") as file:
        data = file.read()

    response._content = data
    response.status_code = 200

    return response
