""" Here's an example how to download all files from our order and then load them into xarray dataset """
from metofficedatahub.multiple_files import MetOfficeDataHub

client_id = "xxx"
client_secret = "yyy"


datahub = MetOfficeDataHub(client_id=client_id, client_secret=client_id)
datahub.download_all_files()
xr = datahub.load_all_files()
