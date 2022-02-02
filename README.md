# Multi Weather API

Consistent Python bindings for select commercial weather station APIs, such as [Zentra Cloud](https://zentracloud.com/) REST API v3, created for MSU EnviroWeather Project.

### Background

This is inspired by python bindings for v1 of the Zentra API from the Montana Climate office : MSU Agricultural Weather Office


The EnviroWeather system from the MSU Agricultural Weather Office will interface with weather stations (select list of vendors) deployed and owned privately. Since each vendor has a differrent REST/Web API to access station's weather data, this package aims to provide a consistent interface to all of those stations in order to make it easy for incoporating them into a data pipeline.

### Installation

The Multi-Weather API is currently available on [PyPI](https://pypi.org/project/multiweatherapi/). Install using `pip`:
```bash
pip install multiweatherapi
```

### Usage

```python
>>> from multiweatherapi import multiweatherapi
>>> param = {'sn': 'STATION_ID',
...          'apikey': 'API_KEY',
...          'apisec': 'API_SECRET'}
>>> resp = multiweatherapi.get_reading('davis', **param)
>>> resp.resp_raw # raw JSON response of the reading
>>> resp.resp_parsed # parsed JSON response into list of dict for EnviroWeather project
```

Refer to the respective link below for parameter and authentication requirements of weather station vendor APIs

- [Zentra](docs/zentra.md)
- [Spectrum](docs/spectrum.md)
- [Onset](docs/onset.md)
- [Davis](docs/davis.md)
- [Rainwise](docs/rainwise.md)
- [Campbell](docs/campbell.md) 

### Supported Python Versions

Python 3.6 and higher are supported.

### Requirements

- [Requests](https://docs.python-requests.org/en/latest/)

### Outputs

To be determined

### License

Released under the MIT License
