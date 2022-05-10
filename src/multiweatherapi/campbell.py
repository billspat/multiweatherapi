from datetime import datetime, timezone
import json
import pytz
from requests import Session, Request


class CampbellParam:
    """
    A class used to represent Campbell API parameters
    Attributes
    ----------
    username : str
        Login account username to campbell-cloud
    user_passwd : str
        Login account password to campbell-cloud
    credentials : dict
        Username and Password dict (internally generated)
    access_token : str
        API access token generated using username & password (internally generated)
    kc_id : str
        Alphanumeric user ID from user details (internally generated)
    organization_id: str
        Alphanumeric organization_id  from user details (internally generated)
    measurements : str
        The name or names of available measurements of the station (comma separated str, internally generated)
    station_id : str
        Alphanumeric ID of the station (for v3 APIs)
    station_lid : str
        Alphanumeric Legacy ID of the station (for v2 APIs)
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
        The path to a local json file to transform
    binding_ver : str
        Python binding version
    """
    def __init__(self, username=None, user_passwd=None, station_id=None, station_lid=None,
                 start_datetime=None, end_datetime=None, tz=None, json_file=None, binding_ver=None):

        self.username = username
        self.user_passwd = user_passwd
        self.credentials = None
        self.access_token = None
        self.kc_id = None
        self.organization_id = None
        self.measurements = ''
        self.station_id = station_id
        self.station_lid = station_lid

        self.start_datetime_org = start_datetime
        self.start_datetime = start_datetime
        self.end_datetime_org = end_datetime
        self.end_datetime = end_datetime
        self.cur_datetime = datetime.now(timezone.utc)
        self.tz = tz
        self.conversion_msg = ''
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()
        self.__get_auth()
        self.__get_ids()
        self.__get_measurements()

    def __check_params(self):
        if self.username is None or not isinstance(self.username, str):
            raise Exception('username must be specified and only str type is supported')
        if self.user_passwd is None or not isinstance(self.user_passwd, str):
            raise Exception('user_passwd must be specified and only str type is supported')
        self.credentials = {'username': self.username, 'password': self.user_passwd}
        if self.station_id is None or self.station_lid is None:
            raise Exception('station_id and station_lid parameters must be included')
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('state_datetime and end_datetime must be specified')
        print("user credentials: {} type - {}".format(type(self.credentials), self.credentials))

    def __utc_to_local(self):
        tzlist = {
            'HT': 'US/Hawaii',
            'AT': 'US/Alaska',
            'PT': 'US/Pacific',
            'MT': 'US/Mountain',
            'CT': 'US/Central',
            'ET': 'US/Eastern'
        }
        print('UTC Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'UTC start date passed as parameter: {}'.format(self.start_datetime) + " \\ "
        self.conversion_msg += 'Campbell utilizes Unix Epoch, just added explicit UTC timezone' + " \\ "
        # self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None) \
        #     if self.start_datetime else None
        self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc) if self.start_datetime else None
        print('Explicit UTC time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Explicit UTC time start date after conversion: {}'.format(self.start_datetime) + " \\ "

        print('UTC End date: {}'.format(self.end_datetime))
        self.conversion_msg += 'UTC end date passed as parameter: {}'.format(self.end_datetime) + " \\ "
        # self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        # if self.end_datetime else None
        self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc) if self.end_datetime else None
        self.conversion_msg += 'Explicit UTC time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        print('Explicit UTC time End date: {}'.format(self.end_datetime))
        # for the metadata
        self.start_datetime_org = \
            self.start_datetime_org.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        self.end_datetime_org = \
            self.end_datetime_org.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        self.cur_datetime = self.cur_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))

    def __format_time(self):
        self.__utc_to_local()
        self.start_datetime = int(self.start_datetime.timestamp()*1000) if self.start_datetime \
            else int(datetime.now().timestamp()*1000)
        self.end_datetime = int(self.end_datetime.timestamp()*1000) if self.end_datetime \
            else int(datetime.now().timestamp()*1000)
        # for metadata
        self.start_datetime_org = self.start_datetime_org.strftime('%Y-%m-%d %H:%M:%S')
        self.end_datetime_org = self.end_datetime_org.strftime('%Y-%m-%d %H:%M:%S')
        self.cur_datetime = self.cur_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def __get_auth(self):
        print('username: \"{}\"'.format(self.username))
        print('user_password: \"{}\"'.format(self.user_passwd))
        request = Request('POST',
                          url='https://api.campbellcloud.io/v3/campbell-cloud/tokens',
                          headers={
                              'Content-Type': 'application/json'},
                          json={'grant_type': 'password',
                                'credentials': self.credentials}).prepare()
        resp = Session().send(request)
        if resp.status_code != 200:
            raise Exception(
                'Get Auth request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code,
                                                                                             resp.text))
        response = resp.json()
        print('Auth response is \"{}\"'.format(response))
        self.access_token = response['access_token']
        print('access_token: \"{}\"'.format(self.access_token))

    def __get_ids(self):
        request = Request('GET',
                          url='https://api.campbellcloud.io/api_v2/user/session',
                          headers={
                              'Authorization': 'Bearer ' + self.access_token
                          }).prepare()
        resp = Session().send(request)
        if resp.status_code != 200:
            raise Exception(
                'Get IDs request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code,
                                                                                            resp.text))
        response = resp.json()
        print('User details are \"{}\"'.format(response))
        self.kc_id = response['kc_id']
        self.organization_id = response['organization_id']
        print('kc_id is \"{}\"'.format(self.kc_id))
        print('organization_id is \"{}\"'.format(self.organization_id))

    def __get_measurements(self):
        path_param = {'organization_id': self.organization_id, 'station_id': self.station_id}
        request = Request('GET',
                          url='https://api.campbellcloud.io/v3/campbell-cloud/organizations'
                              '/{organization_id}/stations/{station_id}/definitions'.format(**path_param),
                          headers={
                              'Authorization': 'Bearer ' + self.access_token},
                          params={'brief': 'true'}).prepare()
        resp = Session().send(request)
        if resp.status_code != 200:
            raise Exception(
                'Get IDs request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code,
                                                                                            resp.text))
        response = resp.json()
        for measurement_data in response:
            self.measurements += measurement_data['name'] + ','
        self.measurements = self.measurements[:-1]
        print('Available measurements are \n{}'.format(self.measurements))


class CampbellReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Campbell server
    response : Response
        a json response from the Campbell server
    transformed_resp : list of dict
        a transformed response from raw JSON file or raw JSON response
    debug_info : dict
        a dict structure consist of parameter name and values
    """

    def __init__(self, param: CampbellParam):
        """
        Gets a device readings using a GET request to the Campbell API.
        Parameters
        ----------
        param : CampbellParam
            CampbellParam object that contains Campbell API parameters
        """
        self.debug_info = {
            'station_lid': param.station_lid,
            'start_datetime_org': param.start_datetime_org,
            'start_datetime': param.start_datetime,
            'end_datetime_org': param.end_datetime_org,
            'end_datetime': param.end_datetime,
            'cur_datetime': param.cur_datetime,
            'tz': param.tz,
            'conversion_msg': param.conversion_msg,
            'measurements': param.measurements,
            'access_token': param.access_token,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__transform()
        elif param.station_lid and param.access_token:
            self.__get(param.station_lid, param.start_datetime, param.end_datetime, param.measurements,
                       param.access_token)
        elif param.station_lid or param.access_token:
            raise Exception('"station_id" and "access_token" parameters must both be included.')
        else:
            # build an empty CampbellToken
            self.request = None
            self.response = None
            self.transformed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, station_lid, epoch_start, epoch_end, measurements, access_token):
        """
        Gets a device readings using a GET request to the Campbell API.
        Wraps build and parse functions.
        Parameters
        ----------
        station_lid : str
            Alphanumeric Legacy ID of the station (for v2 APIs)
        epoch_start : int
            epoch timestamp generated for the beginning of your time period
        epoch_end : int
            epoch timestamp generated for the end of your time period
        measurements : str
            comma separated list of measurements
        access_token : str
            The user's access token for API authorization
        """
        self.__build(station_lid, epoch_start, epoch_end, measurements, access_token)
        self.__make_request()
        self.__transform()
        return self

    def __build(self, station_lid, epoch_start, epoch_end, measurements, access_token):
        """
        Gets a device readings using a GET request to the Campbell API.
        Parameters
        ----------
        station_lid : str
            Alphanumeric Legacy ID of the station (for v2 APIs)
        epoch_start : int
            epoch timestamp generated for the beginning of your time period
        epoch_end : int
            epoch timestamp generated for the end of your time period
        measurements : str
            comma separated list of measurements
        access_token : str
            The user's access token for API authorization
        """
        path_param = {
            'station_id': station_lid,
            'epoch_start': epoch_start,
            'epoch_end': epoch_end,
            'measurements': measurements
        }
        self.request = Request('GET',
                               url='https://api.campbellcloud.io/api_v2/measurement/timeseries'
                                   '/{station_id}/{epoch_start}/{epoch_end}/{measurements}'.format(**path_param),
                               headers={
                                   'Authorization': "Bearer " + access_token}).prepare()
        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Campbell API and stores the response.
        """
        # prep response list
        self.response = list()
        metadata = {
            "vendor": "campbell",
            "station_id": self.debug_info['station_lid'],
            "timezone": self.debug_info['tz'],
            "start_datetime": self.debug_info['start_datetime_org'],
            "end_datetime": self.debug_info['end_datetime_org'],
            "request_time": self.debug_info['cur_datetime'],
            "python_binding_version": self.debug_info['binding_ver']}
        self.response.append(metadata)
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        if resp.status_code != 200:
            raise Exception(
                'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
        elif str(resp.content) == str(b'{"Error": "Device serial number entered does not exist"}'):
            raise Exception(
                'Error: Device serial number entered does not exist')
        self.response.append(resp.json())
        self.debug_info['response'] = self.response
        return self

    def __transform(self):
        """
        Transform the response.
        """
        self.transformed_resp = list()
        # try:
        #     self.device_info = self.response['device']['device_info']
        # except KeyError:
        #     self.device_info = 'N/A'
        # self.timeseries = list(
        #     map(lambda x: CampbellTimeseriesRecord(x), self.response['device']['timeseries']))
        print(self.transformed_resp)
        return self
