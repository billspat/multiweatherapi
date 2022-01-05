from datetime import datetime
import json
from requests import Session, Request


class ZentraParam:
    """
    A class used to represent Zentra API parameters
    Attributes
    ----------
    sn : str
        The serial number of the device
    token : str
        The user's access token
    start_date : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_date : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    start_mrid : int, optional
        Return readings with mrid ≥ start_mrid.
    end_mrid : int, optional
        Return readings with mrid ≤ start_mrid.
    json_file : str, optional
        The path to a local json file to parse.
    """
    def __init__(self, sn=None, token=None, start_date=None, end_date=None, start_mrid=None, end_mrid=None,
                 json_file=None):
        self.sn = sn
        self.token = token
        self.start_date = start_date
        self.end_date = end_date
        self.start_mrid = start_mrid
        self.end_mrid = end_mrid
        self.json_file = json_file

        self.check_params()
        self.format_time()

    def format_time(self):
        self.start_date = self.start_date.strftime('%m-%d-%Y %H:%M') if self.start_date \
            else datetime.now().strftime('%m-%d-%Y %H:%M')
        self.end_date = self.end_date.strftime('%m-%d-%Y %H:%M') if self.end_date \
            else datetime.now().strftime('%m-%d-%Y %H:%M')

    def check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')


class ZentraReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Zentra server
    response : Response
        a json response from the Zentra server
    parsed_resp : list of dict
        a parsed response from
    """

    def __init__(self, param: ZentraParam):
        """
        Gets a device readings using a GET request to the Zentra API.
        Parameters
        ----------
        param : ZentraParam
            ZentraParam object that contains Zentra API parameters
        """
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.parse()
        elif param.sn and param.token:
            self.get(param.sn, param.token, param.start_date, param.end_date, param.start_mrid, param.end_mrid)
        elif param.sn or param.token:
            raise Exception('"sn" and "token" parameters must both be included.')
        else:
            # build an empty ZentraToken
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def get(self, sn, token, start_date=None, end_date=None, start_mrid=None, end_mrid=None):
        """
        Gets a device readings using a GET request to the Zentra API.
        Wraps build and parse functions.
        Parameters
        ----------
        sn : str
            The serial number of the device
        token : str
            The user's access token
        start_date : int, optional
            Return readings with timestamps ≥ start_date.
        end_date : int, optional
            Return readings with timestamps ≤ end_date.
        start_mrid : int, optional
            Return readings with mrid ≥ start_mrid.
        end_mrid : int, optional
            Return readings with mrid ≤ start_mrid.
        """
        self.build(sn, token, start_date, end_date, start_mrid, end_mrid)
        self.make_request()
        self.parse()
        return self

    def build(self, sn, token, start_date=None, end_date=None, start_mrid=None, end_mrid=None):
        """
        Gets a device readings using a GET request to the Zentra API.
        Parameters
        ----------
        sn : str
            The serial number of the device
        token : str
            The user's access token
        start_date : int, optional
            Return readings with timestamps ≥ start_date.
        end_date : int, optional
            Return readings with timestamps ≤ end_date.
        start_mrid : int, optional
            Return readings with mrid ≥ start_mrid.
        end_mrid : int, optional
            Return readings with mrid ≤ start_mrid.
        """
        self.request = Request('GET',
                               url='https://zentracloud.com/api/v3/get_readings',
                               headers={
                                   'Authorization': "Token " + token},
                               params={'sn': sn,
                                       'start_date': start_date,
                                       'end_date': end_date,
                                       'start_mrid': start_mrid,
                                       'end_mrid': end_mrid}).prepare()
        return self

    def make_request(self):
        """
        Sends a token request to the Zentra API and stores the response.
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
        #     map(lambda x: ZentraTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
