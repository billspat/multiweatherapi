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
    This helper method checks to see if a string passed to it is a valid date.

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
    This helper method checks to see if a string passed to it is a valid number.

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
    This helper method returns the values of all the keys in a dictionary.

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

    Yields
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

    Yields
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

    Yields
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
    This test module will test that mwapi correctly handles the situation where the vendor parameters stored in the .env file 
    are missing any required parameters.

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

# The following two tests are for Davis only because:
#    - Davis can only return up to 24 hours worth of data at a time.
#    - There was an error encountered when the start and end times were exactly 24 hours apart.
#
# The purpose of these tests are to make sure any changes to the multiweatherapi library doesn't break the code that
# alleviates these problems.
def test_Davis_exactly_24_Hours(vendor, params):
    """
    The purpose of this test module is to make sure any changes to the multiweatherapi library don't break the code that 
    handles the issues encountered with the Davis API when the start date and end date were exactly 24 hours apart.

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
    The purpose of this test module is to make sure any changes to the multiweatherapi library don't break the code that 
    handles the issues encountered with the Davis API when the requested date range was more than 24 hours.

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
def test_for_missing_parameters(vendor, params):
    """
    This test module will go through all the parameters that are passed to it and remove them one at a time.  The expected result is that
    mwapi catches all instances and places a status_code of 400 in the status_code field of resp_raw and an error message in the
    error_msg field of resp_raw for each missing parameter in each test.
    Example:
       If the parms were A, B, and C, the tests would be as follows: [B, C], [A, C], [A, B]

    Parameters
    ----------
    vendor : str
             The name of the vendor API being tested.
    params : vendor parameter object
             A dictionary of parameters expected by the vendor API
    """

    status_code_fail = ''
    error_msg_fail = ''
    valid_codes = ['400']

    for key in params:
        temp = params.copy()
        temp.pop(key)
        results = multiweatherapi.get_reading(vendor, **temp)
        
        if str(results.resp_raw['status_code']) not in valid_codes:
            status_code_fail += '[' + key + '-' + str(results.resp_raw['status_code']) + '] ' 

        if results.resp_raw['error_msg'] == '':
            error_msg_fail += key + ' - '

    assert status_code_fail == '', 'multiweatherapi failed to set status code for these missing parameters - ' + status_code_fail

    assert error_msg_fail == '', 'multiweatherapi failed to set error message for these missing parameters - ' + status_code_fail

def test_for_bad_parameters(vendor, params):
    """
    This test module will go through all the parameters that are passed to it and one at a time, replace them with bad data. The expected 
    result is that mwapi catches all instances and places a status_code of 400 in the status_code field of resp_raw and an error message 
    in the error_msg field of resp_raw for each bad parameter in each test.
    Example:
       If the parms were A, B, and C, the tests would be as follows: [bad data, B, C], [A, bad data, C], [A, B, bad data]

    Parameters
    ----------
    vendor : str
             The name of the vendor API being tested.
    params : vendor parameter object
             A dictionary of parameters expected by the vendor API
    """

    status_code_fail = ''
    error_msg_fail = ''
    valid_codes = ['400', '401', '403', '404']

    for key in params:
        # If this is a Spectum station and the parameter to be set to bad data is 'sn', then skip as Spectrum stations
        # return empty data if the serial number and en error code of 200 (OK) if invalid instead of an error message, so it would 
        # always fail this test, which looks for 400, 401, 404, and 404.

        if not (key == 'sn' and vendor == 'SPECTRUM'):
            temp = params.copy()
            temp[key] = 'bad_data'
            results = multiweatherapi.get_reading(vendor, **temp)

            if str(results.resp_raw['status_code']) not in valid_codes:
                status_code_fail += '[' + key + '-' + str(results.resp_raw['status_code']) + '] '

            if results.resp_raw['error_msg'] == '' and results.resp_raw:
                error_msg_fail += key + ' - '

    assert status_code_fail == '', 'multiweatherapi failed to set status code when setting bad values for parameters - ' + status_code_fail

    assert error_msg_fail == '', 'multiweatherapi failed to set error message when setting bad values for parameters - ' + status_code_fail

# def test_bad_auth(vendor, params):
#     first_param = list(params.keys())[0]
#     print('first_param = ' + first_param)
#     params[first_param] = 'bad_info'

#     with pytest.raises(Exception) as error:
#         multiweatherapi.get_reading(vendor, **params)


def test_bad_end_datetime(vendor, params):
    """
    The purpose of this test module is to check to make sure mwapi properly handles bad end dates.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.     
    """    
    # Check empty date. 
    # Note: this test commented out until issue #22 has been closed.
    # gitlab URL: https://gitlab.msu.edu/adsdatascience/multiweatherapi/-/issues/22
    # params['end_datetime'] = ""
    # resp = multiweatherapi.get_reading(vendor, **params)  
    # assert resp.resp_raw['error_msg'].__contains__('start_datetime and end_datetime must be specified'), 'End datetime of empty string not caught.'

    params['end_datetime'] = None
    resp = multiweatherapi.get_reading(vendor, **params)  
    assert resp.resp_raw['error_msg'].__contains__('start_datetime and end_datetime must be specified'), 'End datetime of None not caught.'

    params['end_datetime'] = 'This is a bad date'
    resp = multiweatherapi.get_reading(vendor, **params)  
    assert resp.resp_raw['error_msg'].__contains__('end_datetime must be datetime.datetime instance'), 'Non-date end date not caught.'

def test_bad_start_datetime(vendor, params):
    """
    The purpose of this test module is to check to make sure mwapi properly handles bad start dates.

    Parameters
    ----------
    vendor : str
             The vendor we are testing.
    params : vendor parameter object
             The vendor parameter object, which contains the parameteres to be passed to the vendor API.     
    """        
    # Check empty date. 
    # Note: this test commented out until issue #22 has been closed.
    # params['start_datetime'] = ''
    # resp = multiweatherapi.get_reading(vendor, **params)  
    # assert resp.resp_raw['error_msg'].__contains__('start_datetime and end_datetime must be specified'), 'Start datetime of None not caught.'

    params['start_datetime'] = None
    resp = multiweatherapi.get_reading(vendor, **params)  
    assert resp.resp_raw['error_msg'].__contains__('start_datetime and end_datetime must be specified'), 'Start datetime of None not caught.'

    params['start_datetime'] = 'This is a bad date'
    resp = multiweatherapi.get_reading(vendor, **params)  
    assert resp.resp_raw['error_msg'].__contains__('start_datetime must be datetime.datetime instance'), 'Non-date start date not caught.'
 


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

def test_bad_username(vendor, params):
    """
    The purpose of this test is to make sure that mwapi handles missing usernames correctly.  This test is valid only for Campbell and
    Rainwise stations.

    Parameters
    ----------
    vendor : str
             The vendor this test is being run on.
    parms  : vendor parameter object
             The parameters that will be sent to the vendor API.
    """
    # Rainwise and Campbell are the only vendors at this point that have a username field.
    if vendor in ('RAINWISE', 'CAMPBELL'):  
        # Note: this test commented out until issue #22 has been closed.
        # params['username'] = ''
        # resp = multiweatherapi.get_reading(vendor, **params)
        # assert resp.resp_raw['error_msg'].__contains__('username must be specified and only str type is supported')

        params['username'] = 6
        resp = multiweatherapi.get_reading(vendor, **params)
        assert resp.resp_raw['error_msg'].__contains__('username must be specified and only str type is supported') or \
               resp.resp_raw['error_msg'].__contains__('username and mac parameters must be included and same value'), \
               'Incorrect username not caught.'
        
        params['username'] = None
        resp = multiweatherapi.get_reading(vendor, **params)
        assert resp.resp_raw['error_msg'].__contains__('username must be specified and only str type is supported') or \
               resp.resp_raw['error_msg'].__contains__('username and mac parameters must be included and same value'), \
               'username of None not caught.'


def test_start_date_after_end_date(vendor, params):
    """
    The purpose of this test method is to ensure that if the start date is after the end date, the appropriate error message is 
    placed in the error_msg dictionary entry of resp_raw.

    Parameters
    ----------
    params : vendor parameter object
             The parameters that are passed to the vendor API.
    """
    # swap times 
    params['start_datetime'], params['end_datetime'] = params['end_datetime'], params['start_datetime']

    resp = multiweatherapi.get_reading(vendor, **params)
    assert resp.resp_raw['error_msg'].__contains__('start_datetime must be earlier than end_datetime'), \
           'mwapi did not catch that the start date came after the end date'
