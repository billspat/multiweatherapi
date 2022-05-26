# Multiweather API Testing

**NOTE** *currently only the test `tests/test_multiweather_request.py` is functional during this stage of development*

To run the tests, you must clone the package and install the requirements (it doesn't work if you simply pip install the package. )

1. clone this respository into your computer 
1. install requirements including pytest `pip install -r requirements.txt`
1. create a configuration file with station configiuration (see below) called ".env"
1. run tests run from the command line using Pytest, using this syntax:


- run the entire test suite  `pytest` THIS IS CURRENLTY NOT WORKING
- all vendors except Zentra `pytest tests/test_multiweather_request.py `
- one vendor `pytest tests/test_multiweather_request.py --vendor RAINWISE`
- Zentra `pytest tests/test_multiweather_request.py --vendor ZENTRA`
- a combo of the above, plus run all tests whose name contains the keyword. `pytest -k "<keyword>"`
  Example: `pytest tests/test_multiweather_request.py --vendor SPECTRUM -k "content"`

Note Zentra is singled out since it currently has a 60s delay requirement per request and does not pass tests


### Configuration

The test suite expects a .env file to reside in the root directory with  Weather station vendor cloud configuration, for each for each weather station vendor covered by the package. 

The package works with the following vendors, and will use a configuration value for each vendor name as follows (uppercase)

DAVIS, CAMPBELL, ONSET, RAINWISE, SPECTRUM, ZENTRA

Sample:

```
ZENTRA={"sn":"999etc","token":"1a2b3cetc"}
DAVIS={"sn":"99999","apikey":"abcdefgetc","apisec":"x1y2z3etc"}
# etc
```

If a vendor is not present in the configuration file, it will not test for that vendor so that there are not failures for which you don't have configuration. 

After the configuration section will be a section that holds a list of expected configuration values.  This will allow the test suite to check the configuration values it receives form the .env file for any values that might be missing as those could cause subsequent tests to fail.  

Sample:
```
CAMPBELL_PARMS = "station_id,station_lid,username,user_passwd,tz"
DAVIS_PARMS = "sn,apikey,apisec,tz"
ONSET_PARMS = "sn,client_id,client_secret,ret_form,user_id,tz,sensor_sn,atemp,pcpn,relh"
RAINWISE_PARMS = "sn,sid,pid,ret_form,mac,username,tz"
SPECTRUM_PARMS = "sn,apikey,tz"
ZENTRA_PARMS = "sn,token,tz"
```

See https://pypi.org/project/python-dotenv/ for more information on using `.env` files

Each vendor entry is different, and follows documentation for each type in the `/docs` folder of this repository.    