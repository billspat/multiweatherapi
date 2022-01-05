import json
from requests import Session, Request
from datetime import datetime


class SpectrumParam:
    """
    A class used to represent Spectrum API parameters
    Attributes
    ----------
    sn : str
        The serial number of the device
    apikey : str
        The customer's access key
    start_date : datetime
        Return readings for a specific customer device for a specific date-time range.
        (e.g., 2021-08-01 00:00)
    end_date : datetime
        Return readings for a specific customer device for a specific date-time range.
        (e.g., 2021-08-31 23:59)
    date : datetime
        Return readings for a specific date. (e.g., 2021-08-01)
    count : int
        Get a specific number of recent sensor data records for a specific customer device
    json_file : str, optional
        The path to a local json file to parse.
    """
    def __init__(self, sn=None, apikey=None, start_date=None, end_date=None, date=None, count=None, json_file=None):
        self.sn = sn
        self.apikey = apikey
        self.start_date = start_date
        self.end_date = end_date
        self.date = date
        self.count = count
        self.json_file = json_file

        self.check_params()

    def check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.date and not isinstance(self.date, datetime):
            raise Exception('date must be datetime.datetime instance')


class SpectrumReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Spectrum server
    response : Response
        a json response from the Spectrum server
    parsed_resp : list of dict
        a parsed response from
    """
    def __init__(self, param: SpectrumParam):
        """
        Gets a device readings using a GET request to the Spectrum API.

        Parameters
        ----------
        param: SpectrumParam
            SpectrumParam object that contains Spectrum API parameters
        """
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.parse()
        elif param.sn and param.apikey:
            self.get(param.sn, param.apikey, param.start_date, param.end_date, param.date, param.count)
        elif param.sn or param.apikey:
            raise Exception('"sn" and "apikey" parameters must both be included.')
        else:
            # build an empty Spectrum apikey
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def get(self, sn, apikey, start_date=None, end_date=None, date=None, count=None):
        """
        Gets a device readings using a GET request to the Spectrum API.
        Wraps build and parse functions.
        Parameters
        ----------
        sn : str
            The serial number of the device
        apikey : Spectrum apikey
            The user's access apikey
        start_date : datetime
            Return readings for a specific customer device for a specific date/time range.
            (e.g., 2021-08-01, 2021-08-01 00:00)
        end_date : datetime
            Return readings for a specific customer device for a specific date/time range.
            (e.g., 2021-08-31, 2021-08-31 23:59)
        date : datetime
            Return readings for a specific date. (e.g., 2021-08-01)
        count : int
            Get a specific number of recent sensor data records for a specific customer device
        """
        self.build(sn, apikey, start_date, end_date, date, count)
        self.make_request()
        self.parse()
        return self

    def build(self, sn, apikey, start_date=None, end_date=None, date=None, count=None):
        """
        Gets a device readings using a GET request to the Spectrum API.
        Parameters
        ----------
        sn : str
            The serial number of the device
        apikey : Spectrum apikey
            The user's access apikey
        start_date : datetime
            Return readings for a specific customer device for a specific date/time range.
            (e.g., 2021-08-01, 2021-08-01 00:00)
        end_date : datetime
            Return readings for a specific customer device for a specific date/time range.
            (e.g., 2021-08-31, 2021-08-31 23:59)
        date : datetime
            Return readings for a specific date. (e.g., 2021-08-01)
        count : int
            Get a specific number of recent sensor data records for a specific customer device
        """
        if count and count > 0:
            self.request = Request('GET',
                                   url='https://api.specconnect.net:6703/api/Customer/GetDataByRange',
                                   params={'customerApiKey': apikey, 'serialNumber': sn, 'count': count}).prepare()
        elif date:
            self.request = Request('GET',
                                   url='https://api.specconnect.net:6703/api/Customer/GetDataByDate',
                                   params={'customerApiKey': apikey, 'serialNumber': sn, 'date': date}).prepare()
        elif start_date and end_date:
            self.request = Request('GET',
                                   url='https://api.specconnect.net:6703/api/Customer/GetDataInDateTimeRange',
                                   params={'customerApiKey': apikey, 'serialNumber': sn,
                                           'startDate': start_date, 'endDate': end_date}).prepare()
        else:
            self.request = Request('GET',
                                   url='https://api.specconnect.net:6703/api/Customer/GetData',
                                   params={'customerApiKey': apikey, 'serialNumber': sn}).prepare()

        return self

    def make_request(self):
        """
        Sends a token request to the Spectrum API and stores the response.
        """
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        if resp.status_code != 200:
            raise Exception(
                'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
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
        #     map(lambda x: SpectrumTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
