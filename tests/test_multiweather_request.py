from datetime import datetime, timezone, timedelta
import json
import os
import pytest
from src.multiweatherapi import multiweatherapi
import time
from src.multiweatherapi.utilities import Utilities as utilities

# for vendor fixture and dotenv, see conftest.py  

def get_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from get_items(value)
        else:
            yield (key, value)

@pytest.fixture
def expected_vendor_parms(vendor):
    """This will provide a list of parms that a vendor should have in their test package.  Retrieved from the .env file."""

    yield os.environ[vendor.upper() + '_PARMS']


@pytest.fixture
def static_datetimes():
    yield (datetime(2022, 2, 16, 13, 00), datetime(2022, 2, 16, 14, 30))

@pytest.fixture
def recent_datetimes():
    """datetimes range for requesting data, based on current time"""
    start_datetime = datetime.now(timezone.utc) - timedelta(hours=2)
    end_datetime  = start_datetime + timedelta(hours=1)
    yield (start_datetime, end_datetime) 

    
@pytest.fixture
def params(vendor, recent_datetimes):
    """load parameters from .env file keyed on vendor name (upper case)"""
    multiweatherapi_params = json.loads(os.environ[vendor])
    multiweatherapi_params['start_datetime'], multiweatherapi_params['end_datetime'] = recent_datetimes

    yield multiweatherapi_params 


@pytest.fixture
def api_request(vendor, params, scope="session"):
    """ get one request to re-use for multiple tests"""

    readings = multiweatherapi.get_reading(vendor, **params)
    yield readings

def test_vendor_params(vendor, params, expected_vendor_parms):
    # Put expected keys into a list
    expected = expected_vendor_parms.split(',')

    # Get the actual keys from the parms and put them into a list
    actual = []
    for key, value in get_items(params):
        actual.append(key)
    
    missing = []
    for parm in expected:
        if not parm in actual:
            missing.append(parm) 

    assert len(missing) == 0, 'The following parms are missing for the vendor ' + vendor + ': ' + ', '.join(missing)

def test_api_return_some_content(api_request): 
    """ test that we don't get nothing, and it has keys as expected """
    multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes

    assert api_request is not None, "could not get readings at all"
    assert api_request.resp_raw is not None, 'multiweatherapi did not return any raw readings...'

######## test for connection and content
def test_api_return_some_content(vendor, params): 
    """ test that we don't get nothing, and it has keys as expected """
    # multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes
    readings = multiweatherapi.get_reading(vendor, **params)

    assert readings is not None, "could not get readings at all"
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'

def test_resp_raw_contents(vendor, params):
    readings = multiweatherapi.get_reading(vendor, **params)
  
    assert readings is not None, "could not get readings at all"
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'
    assert readings.resp_raw.__contains__('vendor') is True, 'resp_raw is missing a vendor entry...'
    assert readings.resp_raw.__contains__('station_id') is True, 'resp_raw is missing a station_id entry...'
    assert readings.resp_raw.__contains__('timezone') is True, 'resp_raw is missing a timezone entry...'
    assert readings.resp_raw.__contains__('start_datetime') is True, 'resp_raw is missing a start_datetime entry...'
    assert readings.resp_raw.__contains__('end_datetime') is True, 'resp_raw is missing a end_datetime entry...'
    assert readings.resp_raw.__contains__('request_time') is True, 'resp_raw is missing a request_time entry...'
    assert readings.resp_raw.__contains__('python_binding_version') is True, 'resp_raw is missing a python_binding_version entry...'
    assert readings.resp_raw.__contains__('error_msg') is True, 'resp_raw is missing a error_msg entry...'
    assert readings.resp_raw.__contains__('status_code') is True, 'resp_raw is missing a status_code entry...'
    assert readings.resp_raw.__contains__('api_output') is True, 'resp_raw is missing a api_output entry...'

def test_api_transform(vendor, params):
    readings = multiweatherapi.get_reading(vendor, **params)
    assert readings.resp_transformed is not None, 'multiweatherapi did not return any parsed readings...'
    assert readings.resp_transformed, 'multiweatherapi returned an empty transformed data dictionary...'

def test_api_return_valid_content(api_request): 
    resp = api_request.resp_raw
    assert type(resp) ==  type([]), "response is not array type"

# The following tests are for Davis only because:
#    - Davis can only return up to 24 hours worth of data at a time.
#    - There was an error encountered when the start and end times were exactly 24 hours apart.
# The purpose of these tests are to make sure any changes to the multiweatherapi library doesn't break the code that
# alleviates these problems.
def test_Davis_exactly_24_Hours(vendor, params):
    if vendor == 'DAVIS':
        params['end_datetime'] = datetime.now(timezone.utc).replace(microsecond=0)
        params['start_datetime'] = params['end_datetime'] - timedelta(seconds = 86400)
        readings = multiweatherapi.get_reading(vendor, **params)
        assert readings is not None, "Could not get readings at all"
        assert readings.resp_raw is not None, 'Multiweatherapi did not return any raw readings...'         

def test_Davis_More_than_24_hours(vendor, params):
    if vendor == 'DAVIS':   
        params['end_datetime'] = datetime.now(timezone.utc).replace(microsecond=0)
        params['start_datetime'] = params['end_datetime'] - timedelta(days = 2)
        readings = multiweatherapi.get_reading(vendor, **params)
        assert readings is not None, "Could not get readings at all"
        assert readings.resp_raw is not None, 'Multiweatherapi did not return any raw readings...' 


###### tests for bad input handling

# def test_bad_auth(vendor, params):
#     first_param = list(params.keys())[0]
#     print('first_param = ' + first_param)
#     params[first_param] = 'bad_info'

#     with pytest.raises(Exception) as error:
#         multiweatherapi.get_reading(vendor, **params)


def test_bad_end_datetime_raises_exception(vendor, params):
    # break end date pram
    params['end_datetime'] = ""
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)  

    params['end_datetime'] = None
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)  

    params['end_datetime'] = 'This is a bad date'
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)  



def test_bad_start_datetime_raises_exception(vendor, params):
    # break start datetime
    params['start_datetime'] = ''
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)  

    params['start_datetime'] = None
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)  

    params['start_date'] = 'This is a bad date'
    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(**params)  


# def test_bad_params(vendor, params):
#     saved_params = params
#     params['station_id'] = '-bad'
#     with pytest.raises(Exception) as error:
#         multiweatherapi.get_reading(**params)  

#     assert '400' in str(error.value), 'multiweatherapi did not report that ' + params['station_id'] + ' was invalid'

#     params = saved_params
#     params['user_passwd'] = ''

#     with pytest.raises(Exception) as error:
#         readings = multiweatherapi.get_reading(**params)  

#     # assert error.type is Exception,  'multiweatherapi did not catch empty string password'

#     params['user_passwd'] = None

#     with pytest.raises(Exception) as error:
#         readings = multiweatherapi.get_reading(**params)  

#     assert 'user_passwd must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch non-existent password'

#     params['user_passwd'] = 6

#     with pytest.raises(Exception) as error:
#         readings = multiweatherapi.get_reading(**params)  

#     assert 'user_passwd must be specified and only str type is supported' in str(error.value), 'multiweatherapi did not catch non-existent password'

# def test_bad_station_lid(setup):
#     params = loads(os.environ['campbell_good'])
#     params['station_id'] = params.pop('sn')
#     params['station_lid'] = ''
#     params['user_passwd'] = params.pop('password')

#     with pytest.raises(Exception) as error:
#         readings = multiweatherapi.get_reading(**params)  

#     assert '"station_id" and "access_token" parameters must both be included.' in str(error.value), 'multiweatherapi did not catch empty station_lid'

# def test_bad_station_lid_empty(setup):
#     params = loads(os.environ['campbell_good'])
#     params['station_id'] = params.pop('sn')
#     params['station_lid'] = None
#     params['user_passwd'] = params.pop('password')

#     with pytest.raises(Exception) as error:
#         readings = multiweatherapi.get_reading(**params)  

#     assert '"station_id" and "access_token" parameters must both be included.' in str(error.value), 'multiweatherapi did not catch None as station_lid'

def test_bad_username_raises_exception(vendor, params):
    # Rainwise and Campbell are the only vendors at this point that have a username field.
    if vendor in ('RAINWISE', 'CAMPBELL'):  
        params['username'] = '' # Note: This test doesn't work as mwapi doesn't check for the empty string, so an Exception isn't thrown.

        with pytest.raises(Exception) as error:
            multiweatherapi.get_reading(vendor, **params)

        params['username'] = 6
        with pytest.raises(Exception) as error:
            multiweatherapi.get_reading(vendor, **params)
        
        params['username'] = None
        with pytest.raises(Exception) as error:
            multiweatherapi.get_reading(vendor, **params)


def test_start_date_after_end_date_raises_exception(params):
    # swap times 
    params['start_datetime'], params['end_datetime'] = params['end_datetime'], params['start_datetime']

    with pytest.raises(Exception) as error:
        multiweatherapi.get_reading(vendor, **params)    