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
    start_date : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_date : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    json_file : str, optional
        The path to a local json file to parse.
    """
    def __init__(self, sn=None, client_id=None, client_secret=None, ret_form=None, user_id=None, start_date=None,
                 end_date=None, json_file=None):
        self.sn = sn
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.ret_form = ret_form
        self.user_id = user_id
        self.path_param = None
        self.start_date = start_date
        self.end_date = end_date
        self.json_file = json_file

        self.check_params()
        self.format_time()
        self.get_auth()

    def check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.client_id is None or self.client_secret is None:
            raise Exception('client_id and client_secret parameters must be included')
        if self.ret_form is None or self.ret_form != 'JSON':
            raise Exception('ret_form must be specified and currently only \'JSON\' is supported')
        if self.user_id is None or not isinstance(self.user_id, str):
            raise Exception('userId must be specified and only str type is supported')
        self.path_param = {'format': self.ret_form, 'userId': self.user_id}

    def format_time(self):
        self.start_date = self.start_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') if self.start_date \
            else datetime.now().astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.end_date = self.end_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') if self.end_date \
            else datetime.now().astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    def get_auth(self):
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
    """

    def __init__(self, param: OnsetParam):
        """
        Gets a device readings using a GET request to the Onset API.
        Parameters
        ----------
        param : OnsetParam
            OnsetParam object that contains Onset API parameters
        """
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.parse()
        elif param.sn and param.access_token:
            self.get(param.sn, param.access_token, param.path_param, param.start_date, param.end_date)
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

    def get(self, sn, access_token, path_param, start_date, end_date):
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
        start_date : str
            Return readings with timestamps ≥ start_date.
        end_date : str
            Return readings with timestamps ≤ end_date.
        """
        self.build(sn, access_token, path_param, start_date, end_date)
        self.make_request()
        self.parse()
        return self

    def build(self, sn, access_token, path_param, start_date, end_date):
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
        start_date : str
            Return readings with timestamps ≥ start_date.
        end_date : str
            Return readings with timestamps ≤ end_date.
        """
        self.request = Request('GET',
                               url='https://webservice.hobolink.com/ws/data/file/{format}/user/{userId}'.format(
                                   **path_param),
                               headers={
                                   'Authorization': "Bearer " + access_token},
                               params={'loggers': sn,
                                       'start_date_time': start_date,
                                       'end_date_time': end_date}).prepare()
        return self

    def make_request(self):
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
        #     map(lambda x: OnsetTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
