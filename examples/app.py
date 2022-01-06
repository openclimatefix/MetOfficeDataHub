""" Here's an example how to download all files from our order and then load them into xarray dataset """
from metofficeamd.app import MetOfficeAMD

client_id = "xxx"
client_secret = "yyy"


amd = MetOfficeAMD(client_id=client_id, client_secret=client_id)
amd.download_all_files()
xr = amd.load_all_files()
