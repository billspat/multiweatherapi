from datetime import datetime, timezone
import json
from requests import Session, Request


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
    start_date_org : datetime
        Stores datetime object passed initially
    start_date : datetime (UTC expected)
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_date_org : datetime
        Stores datetime object passed initially
    end_date : datetime (UTC expected)
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    conversion_msg : str
        Stores time conversion message
    json_file : str, optional
        The path to a local json file to parse
    binding_ver : str
        Python binding version
    """
    def __init__(self, username=None, sid=None, pid=None, mac=None, ret_form='json', interval=1,
                 start_date=None, end_date=None, json_file=None, binding_ver=None):
        self.username = username
        self.sid = sid
        self.pid = pid
        self.mac = mac
        self.ret_form = ret_form
        self.interval = interval
        self.start_date_org = start_date
        self.start_date = start_date
        self.end_date_org = end_date
        self.end_date = end_date
        self.conversion_msg = ''

        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()

    def __check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise Exception('start_date must be earlier than end_date')
        if self.username is None or self.mac is None or self.username != self.mac:
            raise Exception('username and mac parameters must be included and same value')
        if self.sid is None or self.pid is None or self.sid != self.pid:
            raise Exception('sid and pid parameters must be included and same value')
        if self.ret_form.lower() != 'json' and self.ret_form.lower() != 'xml':
            raise Exception('ret_form must either be json or xml')

    def __utc_to_local(self):
        print('UTC Start date: {}'.format(self.start_date))
        self.conversion_msg += 'UTC start date passed as parameter: {}'.format(self.start_date) + " \\ "
        self.start_date = self.start_date.replace(tzinfo=timezone.utc).astimezone(tz=None) if self.start_date else None
        print('Local time Start date: {}'.format(self.start_date))
        self.conversion_msg += 'Local time start date after conversion: {}'.format(self.start_date) + " \\ "

        print('UTC End date: {}'.format(self.end_date))
        self.conversion_msg += 'UTC end date passed as parameter: {}'.format(self.end_date) + " \\ "
        self.end_date = self.end_date.replace(tzinfo=timezone.utc).astimezone(tz=None) if self.end_date else None
        print('Local time End date: {}'.format(self.end_date))
        self.conversion_msg += 'Local time end date after conversion: {}'.format(self.end_date) + " \\ "

    def __format_time(self):
        self.__utc_to_local()
        self.start_date = self.start_date.strftime('%Y-%m-%d %H:%M:%S') if self.start_date \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.end_date = self.end_date.strftime('%Y-%m-%d %H:%M:%S') if self.end_date \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class RainwiseReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Rainwise server
    response : Response
        a json response from the Rainwise server
    parsed_resp : list of dict
        a parsed response from
    """

    def __init__(self, param: RainwiseParam):
        """
        Gets a device readings using a GET request to the Rainwise API.
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
            'start_date_org': param.start_date_org,
            'start_date': param.start_date,
            'end_date_org': param.end_date_org,
            'end_date': param.end_date,
            'conversion_msg': param.conversion_msg,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__parse()
        elif param.username and param.sid and param.pid and param.mac:
            self.__get(param.username, param.sid, param.pid, param.mac, param.ret_form, param.interval,
                       param.start_date, param.end_date)
        elif param.username or param.sid or param.pid or param.mac:
            raise Exception('"username", "sid", "pid", "mac" parameters must be included.')
        else:
            # build an empty RainwiseToken
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, username, sid, pid, mac, ret_form, interval, start_date=None, end_date=None):
        """
        Gets a device readings using a GET request to the Rainwise API.
        Wraps build and parse functions.
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
        start_date : datetime
            Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
        end_date : datetime
            Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
        """
        self.__build(username, sid, pid, mac, ret_form, interval, start_date, end_date)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, username, sid, pid, mac, ret_form, interval, start_date=None, end_date=None):
        """
        Gets a device readings using a GET request to the Rainwise API.
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
        start_date : datetime
            Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
        end_date : datetime
            Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
        """
        self.request = Request('GET',
                               url='http://api.rainwise.net/main/v1.5/registered/get-historical.php',
                               params={'username': username,
                                       'sid': sid,
                                       'pid': pid,
                                       'mac': mac,
                                       'format': ret_form,
                                       'interval': interval,
                                       'sdate': start_date,
                                       'edate': end_date}).prepare()

        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Rainwise API and stores the response.
        """
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        if resp.status_code != 200:
            raise Exception(
                'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
        elif str(resp.content) == str(b'{"Error": "Device serial number entered does not exist"}'):
            raise Exception(
                'Error: Device serial number entered does not exist')
        self.response = resp.json()
        self.debug_info['response'] = self.response
        self.response['python_binding_version'] = self.debug_info['binding_ver']
        return self

    def __parse(self):
        """
        Parses the response.
        """
        self.parsed_resp = []
        # try:
        #     self.device_info = self.response['device']['device_info']
        # except KeyError:
        #     self.device_info = 'N/A'
        # self.timeseries = list(
        #     map(lambda x: RainwiseTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
