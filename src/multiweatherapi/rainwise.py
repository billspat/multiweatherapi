from datetime import datetime, timezone
import json
import pytz
from requests import Session, Request
from .utilities import Utilities as utilities

class RainwiseParam:
    """
    A class used to represent Rainwise API parameters
    
    Attributes
    ----------
    username : str
        Registered group name (same as MAC)
    sid : str
        Site id, assigned by Rainwise
    pid : str
        Password id, assigned by Rainwise
    mac : str
        MAC of the weather station, Must be in the group assigned to username
    ret_form: str, optional (default json)
        Values xml or json; returns the data as JSON or XML
    interval: int, optional (default 1 min)
        Data aggregation interval, 1, 5, 10, 15, 30, 60 minute intervals
    start_datetime : datetime (UTC expected)
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_datetime : datetime (UTC expected)
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    tz : str
        Time zone information
    conversion_msg : str
        Stores time conversion message
    json_file : str, optional
        The path to a local json file to transform
    binding_ver : str
        Python binding version
    """
    def __init__(self, username=None, sid=None, pid=None, mac=None, ret_form='json', interval=1,
                 start_datetime=None, end_datetime=None, tz=None, json_file=None, binding_ver=None):
        """
        This method initializes a RainwiseParam object.

        Parameters
        ----------
        username       : str
                         Registered group name (same as MAC).
        sid            : str
                         Site id, assigned by Rainwise.
        pid            : str 
                         Password id, assigned by Rainwise.
        mac            : str
                         MAC of the weather station. Must be in the group assigned to username.
        ret_form       : str
                         Values xml or json; returns the data as JSON or XML.
        interval       : int
                         Data aggregation interval (1, 5, 10, 15, 30, 60 minutes).
        start_datetime : datetime
                         The start date of the period being pulled from the API.  Defaults to None. 
        end_datetime   : datetime
                         The end date of the period being pulled from the API.  Defaults to None. 
        tz             : str
                         The time zone.  Defaults to None.
        sensor_sn      : dict
                         A dict of sensor serial numbers.  Defaults to None.
        json_file      : str
                         The path to a local json file to parse.  Defaults to None. 
        binding_ver    : str
                         The python binding version number.  Defaults to None.

        """                 
        self.username = username
        self.sid = sid
        self.pid = pid
        self.mac = mac
        self.ret_form = ret_form
        self.interval = interval
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.cur_datetime = datetime.now(timezone.utc)
        self.tz = tz
        self.conversion_msg = ''

        self.json_file = json_file
        self.binding_ver = binding_ver

    def _process(self):
        """ 
        This method does the following:
        - Checks to make sure all the parameters are present and are of the correct type.
        - Formats dates to local time.
        """           
        self.__check_params()
        self.__format_time()

    def __check_params(self):
        """
        This module is called by _process and checks that all the parameters that go to the API are present and of the
        correct data type.

        Raises
        ------
        Exception
            If any parameter is missing or of an incorrect data type.
        """

        tz_option = ['HT', 'AT', 'PT', 'MT', 'CT', 'ET']
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if self.tz and (self.tz not in tz_option):
            raise Exception('time zone options: HT, AT, PT, MT, CT, ET')
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('start_datetime and end_datetime must be specified')
        if (self.start_datetime or self.end_datetime) and not self.tz:
            raise Exception('if start_datetime or end_datetime is specified, tz must be specified')
        if self.username is None or self.mac is None or self.username != self.mac:
            raise Exception('username and mac parameters must be included and same value')
        if self.sid is None or self.pid is None or self.sid != self.pid:
            raise Exception('sid and pid parameters must be included and same value')
        if not self.ret_form:
            raise Exception('Missing ret_form parameter')
        if self.ret_form.lower() != 'json' and self.ret_form.lower() != 'xml':
            raise Exception('ret_form must either be json or xml')

    def __utc_to_local(self):
        """
        This method converts a datetime object from UTC to the local time zone.
        """

        tzlist = {
            'HT': 'US/Hawaii',
            'AT': 'US/Alaska',
            'PT': 'US/Pacific',
            'MT': 'US/Mountain',
            'CT': 'US/Central',
            'ET': 'US/Eastern'
        }
        print('UTC Start date: {}, local time zone: {}'.format(self.start_datetime, self.tz))
        self.conversion_msg += \
            'UTC start date passed as parameter: {}, local time zone: {}'.format(self.start_datetime, self.tz) + " \\ "
        # self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None) \
        #     if self.start_datetime else None
        self.start_datetime = \
            self.start_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz])) \
            if self.start_datetime else None
        print('Local time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Local time start date after conversion: {}'.format(self.start_datetime) + " \\ "

        print('UTC End date: {}, local time zone: {}'.format(self.end_datetime, self.tz))
        self.conversion_msg += \
            'UTC end date passed as parameter: {}, local time zone: {}'.format(self.end_datetime, self.tz) + " \\ "
        # self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        # if self.end_datetime else None
        self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz])) \
            if self.end_datetime else None
        print('Local time End date: {}'.format(self.end_datetime))
        self.conversion_msg += 'Local time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        self.cur_datetime = self.cur_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))

    def __format_time(self):
        """
        This method makes sure that a datetime object is in the format "YYYY-MM-DD HH:MM:SS".
        """

        self.__utc_to_local()
        self.start_datetime = self.start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.start_datetime \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.end_datetime = self.end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.end_datetime \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cur_datetime = self.cur_datetime.strftime('%Y-%m-%d %H:%M:%S')


class RainwiseReadings:
    """
    A class used to represent a device's readings

    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Rainwise server
    response : list
        a raw json response from the Rainwise server combined with meta data
    transformed_resp : list of dict
        a transformed response from raw JSON file or raw JSON response
    """

    def __init__(self, param: RainwiseParam):
        """
        This method initializes a RainwiseReadings object.

        Parameters
        ----------
        param : RainwiseParam
            RainwiseParam object that contains Rainwise API parameters
        """
        self.debug_info = {
            'username': param.username,
            'sid': param.sid,
            'pid': param.pid,
            'mac': param.mac,
            'ret_form': param.ret_form,
            'interval': param.interval,
            'start_datetime': param.start_datetime,
            'end_datetime': param.end_datetime,
            'cur_datetime': param.cur_datetime,
            'tz': param.tz,
            'conversion_msg': param.conversion_msg,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }

    def _process(self, param: RainwiseParam):
        """ 
        This method does the following:
        - Checks to make sure that the username, sid, pid, and mac parameters are present.
        - If there is a local JSON file to transform, then do so.
        - Gets the readings from the vendor API.

        Raises
        ------
        Exception
            If any of the parameters username, sid, pid, or mac are missing.
        """        
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__transform()
        elif param.username and param.sid and param.pid and param.mac:
            self.__get(param.username, param.sid, param.pid, param.mac, param.ret_form, param.interval,
                       param.start_datetime, param.end_datetime)
        elif param.username or param.sid or param.pid or param.mac:
            raise Exception('"username", "sid", "pid", "mac" parameters must be included.')
        else:
            # build an empty RainwiseToken
            self.request = None
            self.response = None
            self.transformed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, username, sid, pid, mac, ret_form, interval, start_datetime=None, end_datetime=None):
        """
        Gets a device readings from the Rainwise API via these steps:
        1. Call __build to build the request.
        2. Call __make_request to make the actual API call.
        3. Call __transform to transform the API response into JSON.
        
        Parameters
        ----------
        username : str
            Registered group name (may be same as MAC)
        sid : str
            Site id, assigned by Rainwise
        pid : str
            Password id, assigned by Rainwise
        mac : str
            MAC of the weather station, Must be in the group assigned to username
        ret_form: str, optional (default json)
            Values xml or json; returns the data as JSON or XML
        interval: int, optional (default 1 min)
            Data aggregation interval, 1, 5, 10, 15, 30, 60 minute intervals
        start_datetime : datetime
            Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
        end_datetime : datetime
            Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format

        Returns
        -------
        A RainwiseReadings object.
        """
        self.__build(username, sid, pid, mac, ret_form, interval, start_datetime, end_datetime)
        self.__make_request()
        self.__transform()
        return self

    def __build(self, username, sid, pid, mac, ret_form, interval, start_datetime=None, end_datetime=None):
        """
        This method creates the request which will get sent to the API.

        Parameters
        ----------
        username : str
            Registered group name (may be same as MAC)
        sid : str
            Site id, assigned by Rainwise
        pid : str
            Password id, assigned by Rainwise
        mac : str
            MAC of the weather station, Must be in the group assigned to username
        ret_form: str, optional (default json)
            Values xml or json; returns the data as JSON or XML
        interval: int, optional (default 1 min)
            Data aggregation interval, 1, 5, 10, 15, 30, 60 minute intervals
        start_datetime : datetime
            Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
        end_datetime : datetime
            Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format

        Returns
        -------
        A RainwiseReadings object.            
        """
        self.request = Request('GET',
                               url='http://api.rainwise.net/main/v1.5/registered/get-historical.php',
                               params={'username': username,
                                       'sid': sid,
                                       'pid': pid,
                                       'mac': mac,
                                       'format': ret_form,
                                       'interval': interval,
                                       'sdate': start_datetime,
                                       'edate': end_datetime}).prepare()

        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Rainwise API and stores the response.

        Returns
        -------
        A RainwiseReadings object.        
        """
        # prep response list
        self.response = list()
        metadata = {
            "vendor": "rainwise",
            "station_id": self.debug_info['mac'],
            "timezone": self.debug_info['tz'],
            "start_datetime": self.debug_info['start_datetime'],
            "end_datetime": self.debug_info['end_datetime'],
            "request_time": self.debug_info['cur_datetime'],
            "python_binding_version": self.debug_info['binding_ver']}
        self.response.append(metadata)
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        self.response[0]['error_msg'] = ''
        
        if resp.status_code != 200:
            self.response[0]['status_code'] = resp.status_code
            self.response[0]['error_msg'] = utilities.case_insensitive_key(json.loads(resp.text),'Message')
        elif str(resp.content) == str(b'{"Error": "Device serial number entered does not exist"}'):
            self.response[0]['status_code'] = resp.status_code
            self.response[0]['error_msg'] = utilities.case_insensitive_key(json.loads(resp.text),'Message')
        self.response.append(resp.json())
        self.response[0]['status_code'] = resp.status_code
        self.debug_info['response'] = self.response
        return self

    def __transform(self):
        """
        Transform the response into JSON and store it.

        Returns
        -------
        A RainwiseReadings object.            
        """
        self.transformed_resp = utilities.init_transformed_resp(
            'rainwise',
            utilities.local_to_utc(self.debug_info['start_datetime'], self.debug_info['tz']),
            utilities.local_to_utc(self.debug_info['end_datetime'], self.debug_info['tz']))

        resp_timezone = self.response[0]['timezone']
        station_id = self.response[0]['station_id']
        request_datetime = self.response[0]['request_time']
        for idx in range(1, len(self.response)):
            for k, v in self.response[idx]['times'].items():
                temp_dic = {
                    "station_id": station_id,
                    "request_datetime": request_datetime,
                    "data_datetime": utilities.local_to_utc(v, resp_timezone).strftime('%Y-%m-%d %H:%M:%S'),
                    "atemp": round(((float(self.response[idx]['temp'][k]) - 32) * 5 / 9), 2),
                    "pcpn": round((float(self.response[idx]['precip'][k])*25.4), 2),
                    "relh": round(float(self.response[idx]['hum'][k]), 2)
                }
                self.transformed_resp = utilities.insert_resp(self.transformed_resp, temp_dic)
        # print(self.transformed_resp)
        return self
