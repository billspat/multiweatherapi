from datetime import datetime, timezone, timedelta
import json
import os
import pytest
from src.multiweatherapi import multiweatherapi
import time

# for vendor fixture and dotenv, see conftest.py  

@pytest.fixture
def expected_data_keys(vendor):
    """list of expected keys in raw response data.  For Campbell some rand selected keys"""

    # TODO : add expected fields names from json output from each vendor.   
    # better to save this as config rather than hard-code expected outputs in test code
    vendor_keys = {
        'CAMPBELL' :  ['airtemp_c_avg_table5','dewpointtemp_c_avg_table5','windspd_ms_3m_avg_table5','relhum_avg_table5','rain_mm_tot_table5'],
        'DAVIS'    : [], 
        'ONSET'    : [],
        'RAINWISE' : [],
        'SPECTRUM' : [],
        'ZENTRA'   : []
    }

    yield vendor_keys[vendor.upper()]


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
    # If the vendor is Zentra, then sleep for 60 seconds.  This is because Zentra only allows one call every 60 seconds.
    if vendor == 'ZENTRA':
        time.sleep(60)

    readings = multiweatherapi.get_reading(vendor, **params)
    yield readings



def test_api_return_some_content(api_request): # , expected_data_keys
    """ test that we don't get nothing, and it has keys as expected """
    multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes

    assert api_request is not None, "could not get readings at all"
    assert api_request.resp_raw is not None, 'multiweatherapi did not return any raw readings...'



######## test for connection and content
def test_api_return_some_content(vendor, params): # , expected_data_keys
    """ test that we don't get nothing, and it has keys as expected """
    # multiweatherapi_params['start_date'], multiweatherapi_params['end_date'] = recent_datetimes
    readings = multiweatherapi.get_reading(vendor, **params)

    assert readings is not None, "could not get readings at all"
    assert readings.resp_raw is not None, 'multiweatherapi did not return any raw readings...'

def test_api_transform_stubbed(vendor, params):
    if vendor == 'ZENTRA':
        print('###############################')
        time.sleep(60)
    readings = multiweatherapi.get_reading(vendor, **params)
    assert readings.resp_transformed is not None, 'multiweatherapi did not return any parsed readings...'


def test_api_return_valid_content(api_request): # , expected_data_keys
    resp = api_request.resp_raw
    assert type(resp) ==  type([]), "response is not array type"



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
        params['username'] = ''

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




    # data_keys = resp.keys()
    # for k in expected_data_keys:
    #     assert k  in data_keys, f"data element {k} not in respnse data"
    
    # atemp = resp['airtemp_c_avg_table5'][0][1]
    # assert atemp > -50.0
    # assert atemp < 120.0


