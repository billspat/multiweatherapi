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

See https://pypi.org/project/python-dotenv/ for more information on using `.env` files

Each vendor entry is different, and follows documentation for each type in the `/docs` folder of this repository.    