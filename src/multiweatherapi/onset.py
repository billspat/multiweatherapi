from datetime import datetime, timezone
import json
from requests import Session, Request


class OnsetParam:
    """
    A class used to represent Onset API parameters
    Attributes
    ----------
    sn : str
        The serial number of the device
    client_id : str
        client specific value provided by Onset
    client_secret : str
        client specific value provided by Onset
    ret_form : str
        The format data should be returned in. Currently only JSON is supported.
    user_id : str
        numeric ID of the user account This can be pulled from the HOBOlink URL: www.hobolink.com/users/<user_id>
    start_datetime_org : datetime
        Stores datetime object passed initially
    start_datetime : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_datetime_org : datetime
        Stores datetime object passed initially
    end_datetime : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    conversion_msg : str
        Stores time conversion message
    json_file : str, optional
        The path to a local json file to parse.
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, client_id=None, client_secret=None, ret_form=None, user_id=None, start_datetime=None,
                 end_datetime=None, json_file=None, binding_ver=None):
        self.sn = sn
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.ret_form = ret_form
        self.user_id = user_id
        self.path_param = None
        self.start_datetime_org = start_datetime
        self.start_datetime = start_datetime
        self.end_datetime_org = end_datetime
        self.end_datetime = end_datetime
        self.conversion_msg = ''
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()
        self.__get_auth()

    def __check_params(self):
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('state_datetime and end_datetime must be specified')
        if self.client_id is None or self.client_secret is None:
            raise Exception('client_id and client_secret parameters must be included')
        if self.ret_form is None or self.ret_form != 'JSON':
            raise Exception('ret_form must be specified and currently only \'JSON\' is supported')
        if self.user_id is None or not isinstance(self.user_id, str):
            raise Exception('userId must be specified and only str type is supported')
        self.path_param = {'format': self.ret_form, 'userId': self.user_id}

    def __format_time(self):
        # self.start_datetime = self.start_datetime.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        # if self.start_datetime \
        self.start_datetime = self.start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.start_datetime \
            else datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.end_datetime = self.end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.end_datetime \
            else datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.conversion_msg += 'Onset API utilize UTC timestamp as is thus does not require conversion'

    def __get_auth(self):
        print('client_id: \"{}\"'.format(self.client_id))
        print('client_secret: \"{}\"'.format(self.client_secret))
        request = Request('POST',
                          url='https://webservice.hobolink.com/ws/auth/token',
                          headers={
                              'Content-Type': 'application/x-www-form-urlencoded'},
                          data={'grant_type': 'client_credentials',
                                'client_id': self.client_id,
                                'client_secret': self.client_secret}).prepare()
        resp = Session().send(request)
        if resp.status_code != 200:
            raise Exception(
                'Get Auth request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code,
                                                                                             resp.text))
        response = resp.json()
        print('Auth response is \"{}\"'.format(response))
        self.access_token = response['access_token']
        print('access_token: \"{}\"'.format(self.access_token))


class OnsetReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Onset server
    response : Response
        a json response from the Onset server
    parsed_resp : list of dict
        a parsed response from
    debug_info : dict
        a dict structure consist of parameter name and values
    """

    def __init__(self, param: OnsetParam):
        """
        Gets a device readings using a GET request to the Onset API.
        Parameters
        ----------
        param : OnsetParam
            OnsetParam object that contains Onset API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'access_token': param.access_token,
            'path_param': param.path_param,
            'start_datetime_org': param.start_datetime_org,
            'start_datetime': param.start_datetime,
            'end_datetime_org': param.end_datetime_org,
            'end_datetime': param.end_datetime,
            'conversion_msg': param.conversion_msg,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__parse()
        elif param.sn and param.access_token:
            self.__get(param.sn, param.access_token, param.path_param, param.start_datetime, param.end_datetime)
        elif param.sn or param.access_token:
            raise Exception('"sn" and "access_token" parameters must both be included.')
        else:
            # build an empty OnsetToken
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, sn, access_token, path_param, start_datetime, end_datetime):
        """
        Gets a device readings using a GET request to the Onset API.
        Wraps build and parse functions.
        Parameters
        ----------
        sn : str
            The serial number of the device
        access_token : str
            The user's access token generated by OAuth protocol
        path_param : dict
            Path parameters used to formulate the endpoint during runtime
        start_datetime : str
            Return readings with timestamps ≥ start_datetime.
        end_datetime : str
            Return readings with timestamps ≤ end_datetime.
        """
        self.__build(sn, access_token, path_param, start_datetime, end_datetime)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, sn, access_token, path_param, start_datetime, end_datetime):
        """
        Gets a device readings using a GET request to the Onset API.
        Parameters
        ----------
        sn : str
            The serial number of the device
        access_token : str
            The user's access token generated by OAuth protocol
        path_param : dict
            Path parameters used to formulate the endpoint during runtime
        start_datetime : str
            Return readings with timestamps ≥ start_datetime.
        end_datetime : str
            Return readings with timestamps ≤ end_datetime.
        """
        self.request = Request('GET',
                               url='https://webservice.hobolink.com/ws/data/file/{format}/user/{userId}'.format(
                                   **path_param),
                               headers={
                                   'Authorization': "Bearer " + access_token},
                               params={'loggers': sn,
                                       'start_date_time': start_datetime,
                                       'end_date_time': end_datetime}).prepare()
        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Onset API and stores the response.
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
        #     map(lambda x: OnsetTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
