# MetOfficeAMD
Python wrapper around MetOffice Atmospheric Model Data REST API

[![codecov](https://codecov.io/gh/openclimatefix/MetOfficeAMD/branch/main/graph/badge.svg?token=64JOBKZNCI)](https://codecov.io/gh/openclimatefix/MetOfficeAMD)

MetOfficeAMD is a simple wrapper for the API provided by the British Met Office <https://metoffice.apiconnect.ibmcloud.com/metoffice/production/>_ known as Weather DataHub. It can be used to retrieve weather observations and forecasts. The aim is to focus on the AMD - Atmosphere Model Data REST API <https://metoffice.apiconnect.ibmcloud.com/metoffice/production/product/17502/api/16908>

## Access
Your need to register and obtain a API key and secret. This should be placed in environment variables as `API_KEY` and `API_SECRET`

## Python

### Installation

Install directly from pypi using
```pip install metofficeamd```

### Example

```python
from metofficeamd.multiple_files import MetOfficeAMD

# 1. Get data from API, download grip files
amd = MetOfficeAMD(client_id="fake", client_secret="fake")
amd.download_all_files(order_ids=["test_order_id"])

 # 2. load grib files to one Xarray Dataset
data = amd.load_all_files()
```

### Application

You can run it directly with python using 
```bash
python3 metofficeamd/app.py --save-dir="s3://bucket/folder"
```
which will download all the files from NWP, join them together into a xarray dataset, and then save them.

## Docker
The application can be run using docker
### Dockerhub

You can pull the production docker image from docker hub using
```bash
docker pull TODO
```

### local
You can also build your own docker image locally using
```bash
docker build -t metofficeamd -f infrastructure/docker/Dockerfile .
```
and then to run the docker file use
```bash
docker 
```

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
