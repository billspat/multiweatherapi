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
        parms['username'] = parms.pop('user_id')
        parms['mac'] = parms['username']
        parms['pid'] = parms.pop('apisec')
        parms['sid'] = parms.pop('apikey')   

        return parms

    load_dotenv()

    return get_parms  

def test_rainwise_bad_identifier(setup):
    parms = setup('rainwise_good')
    parms['sn'] = parms['sn'] + '-bad'   

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'Device serial number entered does not exist' in str(error.value), 'multiweatherapi did not report an exception'

def test_rainwise_good_identifier(setup):
    parms = setup('rainwise_good')
    readings = multiweatherapi.get_reading(**parms)
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'     

def test_rainwise_empty_end_date(setup):
    parms = setup('rainwise_good')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string end date was invalid'    

def test_rainwise_none_end_date(setup):
    parms = setup('rainwise_good')
    parms['end_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a end date of None was invalid'    

def test_rainwise_string_end_date(setup):
    parms = setup('rainwise_good')
    parms['end_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string end date was invalid'

def test_rainwise_empty_start_date(setup):
    parms = setup('rainwise_good')
    parms['start_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string start date was invalid'    

def test_rainwise_none_start_date(setup):
    parms = setup('rainwise_good')
    parms['start_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a start date of None was invalid'    

def test_rainwise_string_start_date(setup):
    parms = setup('rainwise_good')
    parms['start_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string start date was invalid'    

def test_rainwise_username_empty_string(setup):
    parms = setup('rainwise_good')
    parms['username'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'username and mac parameters must be included and same value' in str(error.value), 'multiweatherapi did not report empty string username as missing'    

def test_rainwise_username_none_value(setup):
    parms = setup('rainwise_good')
    parms['username'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'username and mac parameters must be included and same value' in str(error.value), 'multiweatherapi did not report username with None value as missing'    

def test_rainwise_mac_empty_string(setup):
    parms = setup('rainwise_good')
    parms['mac'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'username and mac parameters must be included and same value' in str(error.value), 'multiweatherapi did not report empty string mac as missing'    

def test_rainwise_mac_none_value(setup):
    parms = setup('rainwise_good')
    parms['mac'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'username and mac parameters must be included and same value' in str(error.value), 'multiweatherapi did not report mac with None value as missing'    

def test_rainwise_mac_and_username_not_equal(setup):
    parms = setup('rainwise_good')
    parms['mac'] = parms['username'] + '-not_equal'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'username and mac parameters must be included and same value' in str(error.value), 'multiweatherapi did not report that username and mac did not match'    

def test_rainwise_ret_form_empty_string(setup):
    parms = setup('rainwise_good')
    parms['ret_form'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The empty string ret_form was not reported as missing'

def test_rainwise_ret_form_None_value(setup):
    parms = setup('rainwise_good')
    parms['ret_form'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The None ret_form was not reported as missing'

def test_rainwise_ret_form_invalid(setup):
    parms = setup('rainwise_good')
    parms['ret_form'] = 'bad value'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The "bad value" ret_form was not reported as incorrect value' 

def test_rainwise_missing_username(setup):
    parms = setup('rainwise_good')
    parms['username'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert '"username", "sid", "pid", "mac" parameters must be included.' in str(error.value), 'Missing username was not reported' 

def test_rainwise_missing_sid(setup):
    parms = setup('rainwise_good')
    parms['sid'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert '"username", "sid", "pid", "mac" parameters must be included.' in str(error.value), 'Missing sid was not reported' 

def test_rainwise_missing_pid(setup):    
    parms = setup('rainwise_good')
    parms['pid'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert '"username", "sid", "pid", "mac" parameters must be included.' in str(error.value), 'Missing pid was not reported' 

def test_rainwise_missing_mac(setup):
    parms = setup('rainwise_good')
    parms['mac'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert '"username", "sid", "pid", "mac" parameters must be included.' in str(error.value), 'Missing mac was not reported' 