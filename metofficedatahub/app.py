""" Application that pulls data from the Metoffice API and saves to a zarr file"""
import logging
import os
from typing import Optional

import click
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_Forecast
from nowcasting_datamodel.read.read import update_latest_input_data_last_updated

from metofficedatahub.multiple_files import MetOfficeDataHub, save

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s:%(message)s")
logging.getLogger("metofficedatahub").setLevel(
    getattr(logging, os.environ.get("LOG_LEVEL", "INFO"))
)

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "INFO")))


@click.command()
@click.option(
    "--api-key",
    default=None,
    envvar="API_KEY",
    help="The API key for MetOffice Weather DataHub",
    type=click.STRING,
)
@click.option(
    "--api-secret",
    default=None,
    envvar="API_SECRET",
    help="The API secret for MetOffice Weather DataHub",
    type=click.STRING,
)
@click.option(
    "--save-dir",
    default=None,
    envvar="SAVE_DIR",
    help="Where to save the zarr files",
    type=click.STRING,
)
@click.option(
    "--db-url",
    default=None,
    envvar="DB_URL",
    help="Database to save when this has run",
    type=click.STRING,
)
@click.option(
    "--order-id",
    "order_ids",
    default=None,
    envvar="ORDER_IDS",
    help="Order IDs from which to pull latest files. "
    "Call flag multiple times to pass multiple IDs, "
    "or space-separate them in the environment variable. "
    "Pulls files from all orders if not provided.",
    multiple=True,
    type=click.STRING,
)
def run(
    api_key,
    api_secret,
    save_dir,
    db_url: Optional[str] = None,
    order_ids: Optional[list[str]] = None,
):
    """Run main application

    1. Get data from API, download grip files
    2. Load grib files to one Xarray Dataset
    3. Save to directory
    4. Update latest data table
    """

    logger.info(f'Running application and saving to "{save_dir}"')
    # 1. Get data from API, download grip files
    datahub = MetOfficeDataHub(client_id=api_key, client_secret=api_secret)
    datahub.download_all_files(order_ids=order_ids)

    # 2. Load grib files to one Xarray Dataset
    data = datahub.load_all_files()

    # 3. Save to directory
    save(dataset=data, save_dir=save_dir)

    # 4. update table to show when this data has been pulled
    if db_url is not None:
        connection = DatabaseConnection(url=db_url, base=Base_Forecast)
        with connection.get_session() as session:
            update_latest_input_data_last_updated(session=session, component="nwp")

    logger.info("Finished Running application.")


if __name__ == "__main__":
    run()
