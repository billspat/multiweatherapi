from datetime import datetime
import json
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
    start_date : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_date : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    json_file : str, optional
        The path to a local json file to parse.
    """
    def __init__(self, username=None, user_passwd=None, station_id=None,
                 station_lid=None, start_date=None, end_date=None, json_file=None):

        self.username = username
        self.user_passwd = user_passwd
        self.credentials = None
        self.access_token = None
        self.kc_id = None
        self.organization_id = None
        self.measurements = ''
        self.station_id = station_id
        self.station_lid = station_lid

        self.start_date = start_date
        self.end_date = end_date
        self.json_file = json_file

        self.check_params()
        self.format_time()
        self.get_auth()
        self.get_ids()
        self.get_measurements()

    def check_params(self):
        if self.username is None or not isinstance(self.username, str):
            raise Exception('username must be specified and only str type is supported')
        if self.user_passwd is None or not isinstance(self.user_passwd, str):
            raise Exception('user_passwd must be specified and only str type is supported')
        self.credentials = {'username': self.username, 'password': self.user_passwd}
        if self.station_id is None or self.station_lid is None:
            raise Exception('station_id and station_lid parameters must be included')
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        print("user credentials: {} type - {}".format(type(self.credentials), self.credentials))

    def format_time(self):
        self.start_date = int(self.start_date.timestamp()*1000) if self.start_date \
            else int(datetime.now().timestamp()*1000)
        self.end_date = int(self.end_date.timestamp()*1000) if self.end_date \
            else int(datetime.now().timestamp()*1000)

    def get_auth(self):
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

    def get_ids(self):
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

    def get_measurements(self):
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
    parsed_resp : list of dict
        a parsed response from
    """

    def __init__(self, param: CampbellParam):
        """
        Gets a device readings using a GET request to the Campbell API.
        Parameters
        ----------
        param : CampbellParam
            CampbellParam object that contains Campbell API parameters
        """
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.parse()
        elif param.station_lid and param.access_token:
            self.get(param.station_lid, param.start_date, param.end_date, param.measurements, param.access_token)
        elif param.station_lid or param.access_token:
            raise Exception('"station_id" and "access_token" parameters must both be included.')
        else:
            # build an empty CampbellToken
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def get(self, station_lid, epoch_start, epoch_end, measurements, access_token):
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
        self.build(station_lid, epoch_start, epoch_end, measurements, access_token)
        self.make_request()
        self.parse()
        return self

    def build(self, station_lid, epoch_start, epoch_end, measurements, access_token):
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
        return self

    def make_request(self):
        """
        Sends a token request to the Campbell API and stores the response.
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
        return self

    def parse(self):
        """
        Parses the response.
        """
        self.parsed_resp = []
        # try:
        #     self.device_info = self.response['device']['device_info']
        # except KeyError:
        #     self.device_info = 'N/A'
        # self.timeseries = list(
        #     map(lambda x: CampbellTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
