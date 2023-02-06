""" Main application for the API wrapper """
import logging
import os

import fsspec
import requests
from pathy import Pathy

from metofficedatahub.constants import DOMAIN, ROOT
from metofficedatahub.models import FileDetails, OrderDetails, OrderList, RunList, RunListForModel

logger = logging.getLogger(__name__)


class BaseMetOfficeDataHub:
    """Main class for connection and retrieving data from Met Office Weather DataHub AMD"""

    def __init__(
        self,
        cache_dir: str = os.getenv("RAW_DIR", "./temp_metofficedatahub"),
        client_id: str = None,
        client_secret: str = None,
    ):
        """
        Initialise the class

        :param cache_dir: The directory where files are downloaded to
        :param client_id: the client id for the api
        :param client_secret: the client secret for the api
        """

        if client_id is None:
            self.client_id = os.environ["API_KEY"]
        else:
            self.client_id = client_id

        if client_secret is None:
            self.client_secret = os.environ["API_SECRET"]
        else:
            self.client_secret = client_secret

        self.make_headers()

        self.cache_dir = cache_dir

    def make_headers(self):
        """
        Make header object
        """
        logger.debug("setting headers to call api")

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
        logger.debug(f"Calling url {url}")

        response = requests.get(url, headers=headers)

        # check response code 200 and show error if not
        logger.debug(response.status_code)
        if response.status_code != 200:
            message = (
                f"Tried to call url but got response code "
                f"{response.status_code} with message: {response.text}"
            )
            logger.debug(message)
            raise Exception(message)

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

    def get_latest_order_file_id(self, order_id, file_id) -> FileDetails:
        """
        Provide the details of a specific file that can be obtained for the latest available data.

        :param order_id: The order ID that you wish to retrieve information about. The Order ID can
            be seen under a specific order on the Atmospheric Weather Data Tool Order Summary Page
            or found in the list of orders in the JSON response from your call to /1.0.0/orders
        :param file_id: The file ID of the application/x-grib file you wish to retrieve information
            about. The file IDs can be seen on the Atmospheric Weather Data Tool Order Summary Page
             or found in the JSON response from your call to /1.0.0/orders/{orderId}/latest
        :return: Pydantic object of the details of the file
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/orders/{order_id}/latest/{file_id}")

        data = response.json()["fileDetails"]

        return FileDetails(**data)

    def get_latest_order_file_id_data(self, order_id, file_id, filename: str = None) -> str:
        """
        Gets the actual data for a specific file that can be obtained for the latest available data.

        :param order_id: The order ID that you wish to retrieve information about. The Order ID can
            be seen under a specific order on the Atmospheric Weather Data Tool Order Summary Page
            or found in the list of orders in the JSON response from your call to /1.0.0/orders
        :param file_id: The file ID of the application/x-grib file you wish to retrieve information
            about. The file IDs can be seen on the Atmospheric Weather Data Tool Order Summary Page
             or found in the JSON response from your call to /1.0.0/orders/{orderId}/latest
        :param filename: the name of the file that will be saved
        :return: filename where the data is downloaded to
        """

        headers = self.headers.copy()
        headers["accept"] = "application/x-grib"

        if filename is None:
            filename = f"{order_id}_{file_id}.grib"

        filename = f"{self.cache_dir}/{filename}"
        fs = fsspec.open(Pathy.fluid(self.cache_dir).parent).fs
        if not fs.exists(filename):
            data = self.call_url(
                url=f"https://{DOMAIN}/{ROOT}/orders/{order_id}/latest/{file_id}/data",
                headers=headers,
            )

            if not fs.isdir(self.cache_dir):
                try:
                    fs.mkdir(self.cache_dir)
                except Exception as e:
                    logger.error(e)
                    raise Exception(
                        f"Could not make directory {self.cache_dir}. "
                        f"Will carry on anyway in case the folder "
                        f"has been made already"
                    )

            with fs.open(filename, mode="wb") as localfile:
                localfile.write(data.content)
        else:
            logger.debug(f"File already exists so not downloading new one, {filename}")

        return filename

    def get_runs(self) -> RunList:
        """
        List all runs

        :return: pydantic object of run list
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/runs")

        data = response.json()

        return RunList(**data)

    def get_runs_model_id(self, model_id) -> RunListForModel:
        """
        List all runs for specific model

        :param model_id: the model id we are looking for
        :return: Pydantic object of specific run list for a model
        """

        response = self.call_url(url=f"https://{DOMAIN}/{ROOT}/runs/{model_id}")

        data = response.json()

        return RunListForModel(**data)
