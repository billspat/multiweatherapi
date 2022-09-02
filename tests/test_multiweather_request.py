from datetime import datetime, timezone, timedelta
import json
import os
import pytest
from src.multiweatherapi import multiweatherapi
import time
from src.multiweatherapi.utilities import Utilities as utilities
import numbers

"""
Pytest Test Suite for MultiweatherAPI (MWAPI)

A set of test modules to test as many of the mwapi functions as possible.
"""
# for vendor fixture and dotenv, see conftest.py  
def is_date(datestring):
    """
    This method checks to see if a string passed to it is a valid date.

    Parameters
    ----------
    datestring : str
                 The string that needs to be verified.

    Returns
    -------
    True if the string is a valid date, otherwise, False.
    """

    from dateutil.parser import parse

    try:
        parse(datestring)
        return True
    except ValueError:
        return False

def is_number(string):
    """
    This method checks to see if a string passed to it is a valid number.

    Parameters
    ----------
    string : str
             The string that needs to be verified.

    Returns
    -------
    True if the string is a valid number, False otherwise.
    """

    try:
        temp = float(string)
        return True
    except ValueError:
        return False

def get_items(dictionary):
    """
    This module returns the values of all the keys in a dictionary.

    Parameters
    ----------
    dictionary : dict
                 The dictionary whose keys we wish to retrieve.

    Returns
    -------
    The keys in a dictionary.             
    """
    
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from get_items(value)
        else:
            yield (key, value)

@pytest.fixture
def expected_vendor_parms(vendor):
    """
    This pytest fixture will provide a list of parms that a vendor should have in their test package.  Retrieved from the .env file.
    
    Parameters
    ----------
    vendor : str
             The vendor whose expected parameters we want to retrieve from the .env file.

    Returns
    -------
    The expected parameters from the .env file.
    """

    yield os.environ[vendor.upper() + '_PARMS']


@pytest.fixture
def static_datetimes():
    """
    This pytest fixture will provide a set start and end date time.
    
    Parameters
    ----------
    None

    Returns
    -------
    A start date of 2022-02-16 13:00:00 and an end date of 2022-02-16 14:30:00.
    """

    yield (datetime(2022, 2, 16, 13, 00), datetime(2022, 2, 16, 14, 30))

@pytest.fixture
def recent_datetimes():
    """
    This pytest fixture returns a datetime range for requesting data, based on current time
    
    Parameters
    ----------
    None

    Returns
    -------
    A start date of the current date/time minus two hours and an end date of the current date/time minus one hour.
    """
    start_datetime = datetime.now(timezone.utc) - timedelta(hours=2)
    end_datetime  = start_datetime + timedelta(hours=1)
    yield (start_datetime, end_datetime) 

    
@pytest.fixture
def params(vendor, recent_datetimes):
    """
    This pytest fixture will load parameters from the .env file keyed on vendor name (upper case).
    
    Parameters
    ----------
    vendor           : str
                       The vendor whose parameters we wish to load.
    recent_datetimes : dictionary
                       The start and end dates, pulled from the recent_datetimes fixture.

    Yields
    ------
    dict 
          The params to be used for testing.
    """
    multiweatherapi_params = json.loads(os.environ[vendor])
    multiweatherapi_params['start_datetime'], multiweatherapi_params['end_datetime'] = recent_datetimes

    yield multiweatherapi_params 


@pytest.fixture
def api_request(vendor, params, scope="session"):
    """ 
    This pytest fixture returns one request that can be reused in multiple tests.
    
    Parameters
    ----------
    vendor : str
             The name of the vendor in upper case.
    params : vendor parameter object.
             The parameters that will get passed to the vendor API.
    scope  : pytest parameter.
             Set to "session", which means the fixture will be available for the entirety of the testing session.

    Yields
    -------
    readings   : vendor readings object
                 The readings that were returned by the vendor API (if any).
    """

    readings = multiweatherapi.get_reading(vendor, **params)
    yield readings

def test_vendor_params(vendor, params, expected_vendor_parms):
    """
    This test module will test that the vendor parameters stored in the .env file are not missing any required parameters.

    Parameters
    ----------
    vendor                : str
                            The vendor to be tested.
    params                : vendor parm object
                            The parameters in the .env file.
    expected_vendor_parms : dictionary
                            The parameters that each vendor API is expecting to see.  Also stored in the .env file.
    """

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

def test_api_return_some_content(vendo): 
    """ 
    This test module verifies that the call to the vendor API returns content.
    
    Parameters
    ----------
    vendo : str
            The vendor whose API is to be tested.
    """
    multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes

    assert api_request is not None, "could not get readings at all"
    assert api_request.resp_raw is not None, 'multiweatherapi did not return any raw readings...'

######## test for connection and content
def test_api_return_some_content(vendor, params): 
    """ 
    This test module verifies that the call to the vendor API returns content.  It is an overridden version of 
    test_api_return_some_content(vendo).
    
    Parameters
    ----------
    vendor : str
             The vendor whose API is to be tested.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.
    """
    # multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes
    readings = multiweatherapi.get_reading(vendor, **params)

    assert readings is not None, "could not get readings at all"
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'

def test_resp_raw_contents(vendor, params):
    """
    This test module checks to make sure that the resp_raw object returned from mwapi has the items that we expect.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.
    """
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
    """
    This test module checks whether or not the transformed data has all the required fields and that they are of the correct data type.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameters to be passed to the vendor API.    
    """  
    readings = multiweatherapi.get_reading(vendor, **params)
    assert readings.resp_transformed is not None, 'multiweatherapi did not return any parsed readings...'
    assert isinstance(readings.resp_transformed, list), 'response is not array type...'
    print(readings.resp_transformed)
    print(len(readings.resp_transformed))
    assert len(readings.resp_transformed) > 0, 'multiweatherapi returned no data...'

    # Loop through all the entries in resp_transformed, checking for the existence of the item and if it is of the correct type.
    index = 1
    
    for data in readings.resp_transformed:
        assert data.__contains__('station_id'), 'Record #' + str(index) + ' is missing a station_id entry...'
        assert data.__contains__('request_datetime'), 'Record #' + str(index) + ' is missing a request_datetime entry...'
        assert data.__contains__('data_datetime'), 'Record #' + str(index) + ' is missing a data_datetime entry...'
        assert data.__contains__('atemp'), 'Record #' + str(index) + ' is missing a atemp entry...'
        assert data.__contains__('pcpn'), 'Record #' + str(index) + ' is missing a pcpn entry...'
        assert data.__contains__('relh'), 'Record #' + str(index) + ' is missing a relh entry...'    
        assert isinstance(data['station_id'], str), 'Record #' + str(index) + ' station_id entry is a ' + str(type(data['station_id'])) + ', not a str...'
        assert is_date(data['request_datetime']), 'Record #' + str(index) + ' request_datetime entry is not a valid datetime object...'
        assert is_date(data['data_datetime']), 'Record #' + str(index) + ' data_datetime entry is not a valid datetime object...'
        assert is_number(data['atemp']), 'Record #' + str(index) + ' atemp entry of *' + str(data['atemp']) + '* is not a valid number...'
        assert is_number(data['pcpn']) , 'Record #' + str(index) + ' pcpn entry *' + str(data['pcpn']) + '* is not a valid number...'
        assert is_number(data['relh']) , 'Record #' + str(index) + ' relh entry *' + str(data['relh']) + '* is not a valid number...'
        index += 1  

# The following tests are for Davis only because:
#    - Davis can only return up to 24 hours worth of data at a time.
#    - There was an error encountered when the start and end times were exactly 24 hours apart.
# The purpose of these tests are to make sure any changes to the multiweatherapi library doesn't break the code that
# alleviates these problems.
def test_Davis_exactly_24_Hours(vendor, params):
    """
    The purpose of this test module is to make sure any changes to the multiweatherapi library doesn't break code necessary to 
    handle the issues encountered with the Davis API when the start date and end date were exactly 24 hours apart.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.     
    """
    if vendor == 'DAVIS':
        params['end_datetime'] = datetime.now(timezone.utc).replace(microsecond=0)
        params['start_datetime'] = params['end_datetime'] - timedelta(seconds = 86400)
        readings = multiweatherapi.get_reading(vendor, **params)
        assert readings is not None, "Could not get readings at all"
        assert readings.resp_raw is not None, 'Multiweatherapi did not return any raw readings...'         

def test_Davis_More_than_24_hours(vendor, params):
    """
    The purpose of this test module is to make sure any changes to the multiweatherapi library doesn't break code necessary to 
    handle the issues encountered with the Davis API when the requested date range was more than 24 hours.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.     
    """
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
    """
    The purpose of this test module to to make sure any changes to the multiweatherapi library doesn't break code necessary to 
    handle the issue encountered with the Davus API when the start date and end date were exactly 24 hours apart.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.     
    """    
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