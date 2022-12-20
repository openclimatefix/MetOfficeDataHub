# MetOfficeDataHub
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
Python wrapper around MetOffice Atmospheric Model Data REST API

[![codecov](https://codecov.io/gh/openclimatefix/MetOfficeDataHub/branch/main/graph/badge.svg?token=64JOBKZNCI)](https://codecov.io/gh/openclimatefix/MetOfficeDataHub)
[![Lint Python](https://github.com/openclimatefix/MetOfficeDataHub/actions/workflows/linters.yaml/badge.svg)](https://github.com/openclimatefix/MetOfficeDataHub/actions/workflows/linters.yaml)

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

You can set the environmental variable `LOG_LEVEL` to define what [log level](https://docs.python.org/3.9/library/logging.html) you would like.

It may also be worth setting 'RAW_DIR' so that the raw files are saved to a certain folder,
and not downloded again if they are already there.

## Docker
The application can be run using docker

You can pull the production docker image from docker hub using
```bash
docker pull openclimatefix/metoffice_weather_datahub
```

### local
You can also build your own docker image locally using
```bash
docker build -t metofficedatahub -f infrastructure/docker/Dockerfile .
```
and then to run the docker file use
```bash
docker run -it -e API_KEY=change -e API_SECRET=change -e SAVE_DIR='save_dir' -e ORDER_IDS='id1 id2 id3' metofficedatahub
```

# Data variables

When the data is loaded they are given a short name. Here is are some common examples:
- lcc   : Low-level cloud cover in %.
- mcc   : Medium-level cloud cover in %.
- hcc   : High-level cloud cover in %.
- sde   : Snow depth in meters.
- dlwrf : Downward longwave radiation flux - ground
- t     : Air temperature at 1 meter above surface in Kelvin.
- r     : Relative humidty in %.
- vis   : Visibility in meters.
- si10  : Wind speed in meters per second, 10 meters above surface.
- prate : Precipitation rate at the surface in kg/m^2/s.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/peterdudfield"><img src="https://avatars.githubusercontent.com/u/34686298?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Peter Dudfield</b></sub></a><br /><a href="https://github.com/openclimatefix/MetOfficeDataHub/commits?author=peterdudfield" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/flowirtz"><img src="https://avatars.githubusercontent.com/u/6052785?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Flo</b></sub></a><br /><a href="https://github.com/openclimatefix/MetOfficeDataHub/commits?author=flowirtz" title="Code">💻</a></td>
    <td align="center"><a href="http://jack-kelly.com"><img src="https://avatars.githubusercontent.com/u/460756?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jack Kelly</b></sub></a><br /><a href="https://github.com/openclimatefix/MetOfficeDataHub/pulls?q=is%3Apr+reviewed-by%3AJackKelly" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://www.jacobbieker.com"><img src="https://avatars.githubusercontent.com/u/7170359?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jacob Bieker</b></sub></a><br /><a href="https://github.com/openclimatefix/MetOfficeDataHub/pulls?q=is%3Apr+reviewed-by%3Ajacobbieker" title="Reviewed Pull Requests">👀</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
