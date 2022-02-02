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

def test_onset_bad_identifier(setup): 
    parms = setup('onset_good')
    parms['client_id'] = parms['client_id'] + '-bad'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '401' in str(error.value), 'multiweatherapi did not report that ' + parms['client_id'] + ' was invalid'

def test_onset_good_identifier(setup): 
    parms = setup('onset_good')

    readings = multiweatherapi.get_reading(**parms)
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'   

def test_onset_empty_end_date(setup):
    parms = setup('onset_good')
    parms['end_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string end date was invalid'    

def test_onset_none_end_date(setup):
    parms = setup('onset_good')
    parms['end_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a end date of None was invalid'    

def test_onset_string_end_date(setup):
    parms = setup('onset_good')
    parms['end_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string end date was invalid'

def test_onset_empty_start_date(setup):
    parms = setup('onset_good')
    parms['start_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string start date was invalid'    

def test_onset_none_start_date(setup):
    parms = setup('onset_good')
    parms['start_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a start date of None was invalid'    

def test_onset_string_start_date(setup):
    parms = setup('onset_good')
    parms['start_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string start date was invalid'    

def test_onset_client_id_empty_string(setup):
    parms = setup('onset_good')
    parms['client_id'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'client_id and client_secret parameters must be included' in str(error.value), 'multiweatherapi did not report empty string client_id as missing'    

def test_onset_client_id_none_value(setup):
    parms = setup('onset_good')
    parms['client_id'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'client_id and client_secret parameters must be included' in str(error.value), 'multiweatherapi did not report client_id with None value as missing'    

def test_onset_client_secret_empty_string(setup):
    parms = setup('onset_good')
    parms['client_secret'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'client_id and client_secret parameters must be included' in str(error.value), 'multiweatherapi did not report empty string client_secret as missing'    

def test_onset_client_secret_none_value(setup):
    parms = setup('onset_good')
    parms['client_secret'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'client_id and client_secret parameters must be included' in str(error.value), 'multiweatherapi did not report client_secret with None value as missing'    

def test_onset_ret_form_empty_string(setup):
    parms = setup('onset_good')
    parms['ret_form'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The empty string ret_form was not reported as missing'

def test_onset_ret_form_None_value(setup):
    parms = setup('onset_good')
    parms['ret_form'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The None ret_form was not reported as missing'

def test_onset_ret_form_invalid(setup):
    parms = setup('onset_good')
    parms['ret_form'] = 'bad value'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)    

    assert 'ret_form must be specified and currently only' in str(error.value), 'The "bad value" ret_form was not reported as incorrect value' 

def test_onset_user_id_empty_string(setup):
    parms = setup('onset_good')
    parms['user_id'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert 'userId must be specified and only str type is supported' in str(error.value), 'The empty string user_id was not reported as missing'

def test_onset_user_id_None_value(setup):
    parms = setup('onset_good')
    parms['user_id'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert 'userId must be specified and only str type is supported' in str(error.value), 'The None value user_id was not reported as missing'   

def test_onset_user_id_not_string(setup):
    parms = setup('onset_good')
    parms['user_id'] = 6

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert 'userId must be specified and only str type is supported' in str(error.value), 'The int value user_id was not reported as incorrect'  

def test_onset_missing_sn(setup):
    parms = setup('onset_good')
    parms['sn'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert '"sn" and "access_token" parameters must both be included.' in str(error.value), 'sn with value of None was not reported as missing'  

def test_onset_empty_string_sn(setup):
    parms = setup('onset_good')
    parms['sn'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert '"sn" and "access_token" parameters must both be included.' in str(error.value), 'sn with value of the empty string was not reported as missing' 

def test_onset_missing_access_token(setup):
    parms = setup('onset_good')
    parms['access_token'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert '"sn" and "access_token" parameters must both be included.' in str(error.value), 'access_token with value of None was not reported as missing'  

def test_onset_empty_string_access_token(setup):
    parms = setup('onset_good')
    parms['access_token'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms) 

    assert '"sn" and "access_token" parameters must both be included.' in str(error.value), 'access_token with value of the empty string was not reported as missing'     

def test_onset_start_date_after_end_date(setup):
    parms = setup('onset_good')
    temp = parms['start_date']
    parms['start_date'] = parms['end_date']
    parms['end_date'] = temp

    print('start date = ' + str(parms['start_date']) + ', end date = ' + str(parms['end_date']))
    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)       