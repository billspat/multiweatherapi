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
        parms['end_date'] = datetime.now()#.replace(tzinfo = local)
        parms['start_date'] = datetime.now() - timedelta(seconds = 86400)

        return parms

    load_dotenv()

    return get_parms

def test_davis_bad_identifier(setup):
    parms = setup('campbell_good')
    parms['sn'] = parms['sn'] + '-bad'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '404' in str(error.value), 'multiweatherapi did not report that ' + parms['sn'] + ' was invalid'

def test_davis_apikey_empty_string(setup):
    parms = setup('campbell_good')
    parms['apikey'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"apikey" and "apisec" parameters must both be included.' in str(error.value), 'multiweatherapi did not report an empty apikey as missing.'    

def test_davis_apikey_None_value(setup):
    parms = setup('campbell_good')
    parms['apikey'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"apikey" and "apisec" parameters must both be included.' in str(error.value), 'multiweatherapi did not report an None apikey as missing.'    

def test_davis_apisec_empty_string(setup):
    parms = setup('campbell_good')
    parms['apisec'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"apikey" and "apisec" parameters must both be included.' in str(error.value), 'multiweatherapi did not report an empty apisec as missing.'    

def test_davis_apisec_None_value(setup):
    parms = setup('campbell_good')
    parms['apisec'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"apikey" and "apisec" parameters must both be included.' in str(error.value), 'multiweatherapi did not report an None apisec as missing.'

def test_davis_good_identifier(setup):
    parms = setup('campbell_good')

    readings = multiweatherapi.get_reading(**parms)
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'    

def test_davis_empty_end_date(setup):
    parms = setup('campbell_good')
    parms['end_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string end date was invalid'    

def test_davis_empty_string_sn(setup):
    parms = setup('campbell_good')
    parms['sn'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"sn" parameter must be included' in str(error.value), 'multiweatherapi did not report that an empty string sn was invalid'    

def test_davis_none_sn(setup):
    parms = setup('campbell_good')
    parms['sn'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"sn" parameter must be included' in str(error.value), 'multiweatherapi did not report that a None sn was invalid' 

def test_davis_none_end_date(setup):
    parms = setup('campbell_good')
    parms['end_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a end date of None was invalid'    

def test_davis_string_end_date(setup):
    parms = setup('campbell_good')
    parms['end_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string end date was invalid'

def test_davis_empty_start_date(setup):
    parms = setup('campbell_good')
    parms['start_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string start date was invalid'    

def test_davis_none_start_date(setup):
    parms = setup('campbell_good')
    parms['start_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a start date of None was invalid'    

def test_davis_string_start_date(setup):
    parms = setup('campbell_good')
    parms['start_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string start date was invalid'    

def test_davis_start_date_after_end_date(setup):
    parms = setup('davis_good')
    temp = parms['start_date']
    parms['start_date'] = parms['end_date']
    parms['end_date'] = temp

    print('start date = ' + str(parms['start_date']) + ', end date = ' + str(parms['end_date']))
    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)       