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

def test_zentra_bad_identifier(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    parms['sn'] = parms['sn'] + '-bad'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)  

    assert '404' in str(error.value), 'multiweatherapi did not report that ' + parms['sn'] + ' was invalid'

def test_zentra_good_identifier(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    readings = multiweatherapi.get_reading(**parms)
    
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_parsed is not None, 'multiweatherapi did not return any parsed readings...'  

def test_zentra_non_date_start_date(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    parms['start_date'] = 'bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report string start date as invalid'

def test_zentra_non_date_end_date(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    parms['end_date'] = 'bad date'

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert 'date must be datetime.datetime instance' in str(error.value), 'multiweatherapi did not report string end date as invalid'

def test_zentra_missing_sn(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    parms['sn'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert '"sn" and "token" parameters must both be included' in str(error.value), 'multiweatherapi did not report missing sn parm'

def test_zentra_missing_token(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    parms['token'] = None

    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

    assert '"sn" and "token" parameters must both be included' in str(error.value), 'multiweatherapi did not report missing token parm'    

def test_zentra_start_date_after_end_date(setup):
    # Wait 70 seconds to get around Zentra's one call per minute restriction.
    time.sleep(70)
    parms = setup('zentra_good')
    temp = parms['start_date']
    parms['start_date'] = parms['end_date']
    parms['end_date'] = temp

    print('start date = ' + str(parms['start_date']) + ', end date = ' + str(parms['end_date']))
    with pytest.raises(Exception) as error:
        readings = multiweatherapi.get_reading(**parms)

def test_zentra_one_day(setup):
    parms = setup('zentra_good')
    parms['station_id'] = parms.pop('sn')
    parms['station_lid'] = parms.pop('client_id')
    parms['user_passwd'] = parms.pop('password')    
    parms['start_date'] = datetime(2022, 2, 16, 13, 00)
    parms['end_date'] = datetime(2022, 2, 16, 14, 30)
    readings = multiweatherapi.get_reading(**parms)
    print(readings.resp_raw)     