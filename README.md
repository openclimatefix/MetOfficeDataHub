# MetOfficeDataHub
Python wrapper around MetOffice Atmospheric Model Data REST API

[![codecov](https://codecov.io/gh/openclimatefix/MetOfficeAMD/branch/main/graph/badge.svg?token=64JOBKZNCI)](https://codecov.io/gh/openclimatefix/MetOfficeAMD)

MetOfficeDataHub is a simple wrapper for [the API provided by the British Met Office](https://metoffice.apiconnect.ibmcloud.com/metoffice/production/) known as Weather DataHub.
It can be used to retrieve weather observations and forecasts. The aim is to focus on the AMD -
Atmosphere Model Data REST API
<https://metoffice.apiconnect.ibmcloud.com/metoffice/production/product/17502/api/16908>

This wrapper currently only downloads the latest results. No historic data can be fetched.
The timestamp can be seen in the grib/xarray files.

> ⚠️ This (unofficial) library has been built and is maintained by [Open Climate Fix](https://openclimatefix.org), not the [UK MetOffice](https://www.metoffice.gov.uk/).

## Access
You [need to register with the Weather DataHub](https://metoffice.apiconnect.ibmcloud.com/metoffice/production/user/login) and obtain an API key and secret. These should be placed in environment variables
as `API_KEY` and `API_SECRET`.

## Python

### Installation

Install directly from pypi using
```pip install metoffice-weather-datahub```

### Example

```python
from metofficedatahub.multiple_files import MetOfficeDataHub

# 1. Get data from API, download grib files
datahub = MetOfficeDataHub(client_id="fake", client_secret="fake")
datahub.download_all_files(order_ids=["test_order_id"])

# 2. load grib files to one Xarray Dataset
data = datahub.load_all_files()
```

### CLI

You can run the script directly as a CLI using:
```bash
python3 metofficedatahub/app.py --save-dir="s3://bucket/folder"
```
which will download all the files from Weather DataHub, join them together into a xarray dataset, and then save them.

## Docker

TODO

# Data variables

When the data is loaded they are given a short name. Here is are some common examples:
- lcc   : Low-level cloud cover in %.
- mcc   : Medium-level cloud cover in %.
- hcc   : High-level cloud cover in %.
- sde   : Snow depth in meters.
- dswrf : Downward longwave radiation flux - ground
- t     : Air temperature at 1 meter above surface in Kelvin.
- r     : Relative humidty in %.
- vis   : Visibility in meters.
- si10  : Wind speed in meters per second, 10 meters above surface.
- prate : Precipitation rate at the surface in kg/m^2/s.
