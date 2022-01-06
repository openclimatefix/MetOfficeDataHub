""" Application that pulls data from the Metoffice API and saves to a zarr file"""
import logging

import click

from metofficeamd.multiple_files import MetOfficeAMD, save_to_zarr

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--api-key",
    default=None,
    envvar="API_KEY",
    help="The API key for MetOffice Weather DataHub AMD",
    type=click.STRING,
)
@click.option(
    "--api-secret",
    default=None,
    envvar="API_SECRET",
    help="The API secret for MetOffice Weather DataHub AMD",
    type=click.STRING,
)
@click.option(
    "--save-dir",
    default=None,
    envvar="SAVE_DIR",
    help="Where to save the zarr files",
    type=click.STRING,
)
def run(api_key, api_secret, save_dir):
    """Run main application

    1. Get data from API, download grip files
    2. load grib files to one Xarray Dataset
    3. Save to directory
    """

    # 1. Get data from API, download grip files
    amd = MetOfficeAMD(client_id=api_key, client_secret=api_secret)
    amd.download_all_files()

    # 2. load grib files to one Xarray Dataset
    data = amd.load_all_files()

    # 3. Save to directory
    save_to_zarr(dataset=data, save_dir=save_dir)


if __name__ == "__main__":
    run()
