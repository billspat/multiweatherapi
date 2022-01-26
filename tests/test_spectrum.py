import ast
from datetime import datetime, timedelta
from json import loads
from dotenv import load_dotenv
from multiweatherapi import multiweatherapi
import os
from pprint import pprint
import pytest
import time

@pytest.fixture(scope = 'session')
def setup():
    def get_parms(key):
        parms = loads(os.environ[key])
        parms['end_date'] = datetime.now()
        parms['start_date'] = datetime.now() - timedelta(seconds = 86400)

        return parms

    load_dotenv()

    return get_parms  

def test_spectrum_bad_identifier(setup):
    parms = setup('spectrum_good')
    parms['sn'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"sn" and "apikey" parameters must both be included.' in str(error.value), 'multiweatherapi did not report that ' + parms['sn'] + ' was invalid'

def test_spectrum_good_identifier(setup):
    parms = setup('spectrum_good')
    
    readings = multiweatherapi.get_reading(**parms)
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'   

def test_spectrum_non_datetime_start_date(setup):
    parms = setup('spectrum_good')
    parms['start_date'] = 'fred'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that empty string start date was not a string'

def test_spectrum_non_datetime_end_date(setup):
    parms = setup('spectrum_good')
    parms['end_date'] = 'fred'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that empty string end date was not a string'

def test_spectrum_non_datetime_date(setup):
    parms = setup('spectrum_good')
    parms['date'] = 'fred'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that empty string date was not a string'

def test_spectrum_missing_sn(setup):
    parms = setup('spectrum_good')    
    parms['sn'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert '"sn" and "apikey" parameters must both be included.' in str(error.value), 'multiweather did not report missing sn'

def test_spectrum_missing_apikey(setup):
    parms = setup('spectrum_good')    
    parms['apikey'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert '"sn" and "apikey" parameters must both be included.' in str(error.value), 'multiweather did not report missing apikey'    