# MetOfficeAMD
Python wrapper around MetOffice Atmospheric Model Data REST API

[![codecov](https://codecov.io/gh/openclimatefix/MetOfficeAMD/branch/main/graph/badge.svg?token=64JOBKZNCI)](https://codecov.io/gh/openclimatefix/MetOfficeAMD)

IN DEVELOPMENT

MetOfficeAMD is a simple wrapper for the API provided by the British Met Office <https://metoffice.apiconnect.ibmcloud.com/metoffice/production/>_ known as Weather DataHub. It can be used to retrieve weather observations and forecasts. The aim is to forecus on the AMD - Atmosphere Model Data REST API <https://metoffice.apiconnect.ibmcloud.com/metoffice/production/product/17502/api/16908>

## Access
Your need to register and obtain a API key and secret. This should be placed in environment variables as `API_KEY` and `API_SECRET`

## Installation

```pip install metofficeamd```


# Data variables

When the data is loaded they are given a short name
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
