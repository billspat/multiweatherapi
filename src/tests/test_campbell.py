import ast
from datetime import datetime, timedelta
from json import loads
from dotenv import load_dotenv
from multiweatherapi import multiweatherapi
import os
from pprint import pprint
import pytest

@pytest.fixture(scope = 'session')
def setup():
    def get_parms(key):
        parms = loads(os.environ[key])
        parms['end_date'] = datetime.now()#.replace(tzinfo = local)
        parms['start_date'] = datetime.now() - timedelta(seconds = 86400)

        return parms

    load_dotenv()

    return get_parms

def test_campbell_bad_auth(setup):
    parms = setup('campbell_good')
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')    
    parms['username'] = 'bad_user'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'Get Auth request failed with' in str(error.value), 'multiweatherapi did not return a auth request failure error returned ' + str(error.value)

def test_campbell_empty_end_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['end_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string end date was invalid'    

def test_campbell_none_end_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['end_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a end date of None was invalid'    

def test_campbell_string_end_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['end_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'end_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string end date was invalid'

def test_campbell_empty_start_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['start_date'] = str('')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that an empty string start date was invalid'    

def test_campbell_none_start_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['start_date'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a start date of None was invalid'    

def test_campbell_string_start_date(setup):
    parms = setup('campbell_good')
    # parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['start_date'] = 'This is a bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'start_date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report that a string start date was invalid'    

def test_campbell_bad_identifier(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn') + '-bad'
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '400' in str(error.value), 'multiweatherapi did not report that ' + parms['station_id'] + ' was invalid'

def test_campbell_bad_password(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn') + '-bad'
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'user_passwd must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch empty string password'

    parms['user_passwd'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'user_passwd must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch non-existent password'

    parms['user_passwd'] = 6

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert 'user_passwd must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch non-existent password'

def test_campbell_bad_station_lid(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = ''
    parms['user_passwd'] = parms.pop('password')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"station_id" and "access_token" parameters must both be included.' in str(error.value), 'multiweatherapi did not catch empty station_lid'

def test_campbell_bad_station_lid_empty(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = None
    parms['user_passwd'] = parms.pop('password')

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '"station_id" and "access_token" parameters must both be included.' in str(error.value), 'multiweatherapi did not catch None as station_lid'

def test_campbell_bad_username(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')
    parms['username'] = ''

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'username must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch a blank username'

    parms['username'] = 6
    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'username must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not report error with username not being a string'
     
    parms['username'] = None
    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'username must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not report error with username not being a string'

def test_campbell_good_identifier(setup):
    parms = loads(os.environ['campbell_good'])
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')

    readings = multiweatherapi.get_reading(**parms)
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'