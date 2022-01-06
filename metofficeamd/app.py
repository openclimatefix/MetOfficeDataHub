import http.client
import os
import requests

from metofficeamd.constants import DOMAIN, ROOT
from metofficeamd.models import FileDetails, OrderDetails, OrderList, RunList, RunListForModel


class MetOfficeAMD:
    """Main class for connection and retrieving data from Met Office Weather DataHub AMD"""

    def __init__(
        self,
        cache_dir: str = "./temp_metofficeamd",
        client_id: str = None,
        client_secret: str = None,
    ):

        if client_id is None:
            self.client_id = os.environ["API_KEY"]
        else:
            # add warning
            self.client_id = client_id

        if client_secret is None:
            self.client_secret = os.environ["API_SECRET"]
        else:
            # add warning
            self.client_secret = client_secret

        self.make_connection()
        self.make_headers()

        self.cache_dir = cache_dir

    def make_connection(self):
        self.conn = http.client.HTTPSConnection(DOMAIN)

    def make_headers(self):
        self.headers = {
            "X-IBM-Client-Id": self.client_id,
            "X-IBM-Client-Secret": self.client_secret,
            "accept": "application/json",
        }

    def call_url(self, url: str, headers: dict = None) -> requests.Response:
        """
        Call url string using request library.

        :param url: url to be called
        :return: response from url
        """
        if headers is None:
            headers = self.headers

        url = f"{url}?detail=MINIMAL"

        response = requests.get(url, headers=self.headers)

        # check response code 200 and show error if not

        return response

    def get_orders(self) -> OrderList:
        """Get a list of order"""

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/orders")

        data = response.json()

        return OrderList(**data)

    def get_lastest_order(self, order_id) -> OrderDetails:
        """
        Provide a list of the latest available data files for the specified order.

        :param order_id: The order ID that you wish to retrieve information about. The Order ID can
            be seen under a specific order on the Atmospheric Weather Data Tool Order Summary Page
            or found in the list of orders in the JSON response from your call to /1.0.0/orders
        :return: The latest order
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/orders/{order_id}/latest")

        data = response.json()["orderDetails"]

        return OrderDetails(**data)

    def get_lastest_order_file_id(self, order_id, file_id) -> FileDetails:
        """
        Provide the details of a specific file that can be obtained for the latest available data.

        :param order_id: The order ID that you wish to retrieve information about. The Order ID can
            be seen under a specific order on the Atmospheric Weather Data Tool Order Summary Page
            or found in the list of orders in the JSON response from your call to /1.0.0/orders
        :param file_id: The file ID of the application/x-grib file you wish to retrieve information
            about. The file IDs can be seen on the Atmospheric Weather Data Tool Order Summary Page
             or found in the JSON response from your call to /1.0.0/orders/{orderId}/latest
        :return:
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/orders/{order_id}/latest/{file_id}")

        data = response.json()["fileDetails"]

        return FileDetails(**data)

    def get_lastest_order_file_id_data(self, order_id, file_id) -> str:
        """
        Gets the actual data for a specific file that can be obtained for the latest available data.

        :param order_id: The order ID that you wish to retrieve information about. The Order ID can
            be seen under a specific order on the Atmospheric Weather Data Tool Order Summary Page
            or found in the list of orders in the JSON response from your call to /1.0.0/orders
        :param file_id: The file ID of the application/x-grib file you wish to retrieve information
            about. The file IDs can be seen on the Atmospheric Weather Data Tool Order Summary Page
             or found in the JSON response from your call to /1.0.0/orders/{orderId}/latest
        :return:
        """

        headers = self.headers
        headers["Accept"] = "application/x-grib"
        headers["accept"] = "application/x-grib"
        data = self.call_url(
            url=f"https://{DOMAIN}/{ROOT}/orders/{order_id}/latest/{file_id}/data",
            headers=headers,
        )

        filename = f"{self.cache_dir}/{order_id}_{file_id}.grib"
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

        with open(filename, mode="wb") as localfile:
            localfile.write(data.content)

        return filename

    def get_runs(self) -> RunList:
        """
        List all runs

        :return:
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/runs")

        data = response.json()

        return RunList(**data)

    def get_runs_model_id(self, model_id) -> RunListForModel:
        """

        :param model_id:
        :return:
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/runs/{model_id}")

        data = response.json()

        return RunListForModel(**data)
