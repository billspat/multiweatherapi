import json
from requests import Session, Request
from datetime import datetime, timezone


class SpectrumParam:
    """
    A class used to represent Spectrum API parameters
    Attributes
    ----------
    sn : str
        The serial number of the device
    apikey : str
        The customer's access key
    start_date_org : datetime
        Stores datetime object passed initially
    start_date : datetime
        Return readings for a specific customer device for a specific date-time range.
        (e.g., 2021-08-01 00:00)
    end_date_org : datetime
        Stores datetime object passed initially
    end_date : datetime
        Return readings for a specific customer device for a specific date-time range.
        (e.g., 2021-08-31 23:59)
    date_org : datetime
        Stores datetime object passed initially
    date : datetime
        Return readings for a specific date. (e.g., 2021-08-01)
    conversion_msg : str
        Stores time conversion message
    count : int
        Get a specific number of recent sensor data records for a specific customer device
    json_file : str, optional
        The path to a local json file to parse.
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, apikey=None, start_date=None, end_date=None, date=None, count=None, json_file=None,
                 binding_ver=None):
        self.sn = sn
        self.apikey = apikey
        self.start_date_org = start_date
        self.start_date = start_date
        self.end_date_org = end_date
        self.end_date = end_date
        self.date_org = date
        self.date = date
        self.conversion_msg = ''
        self.count = count
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__utc_to_local()

    def __check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise Exception('start_date must be earlier than end_date')
        if self.date and not isinstance(self.date, datetime):
            raise Exception('date must be datetime.datetime instance')

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

        print('UTC date: {}'.format(self.date))
        self.conversion_msg += 'UTC date passed as parameter: {}'.format(self.date) + " \\ "
        self.date = self.date.replace(tzinfo=timezone.utc).astimezone(tz=None) if self.date else None
        print('Local time date: {}'.format(self.date))
        self.conversion_msg += 'Local time date after conversion: {}'.format(self.end_date) + " \\ "


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
    debug_info : dict
        a dict structure consist of parameter name and values
    """
    def __init__(self, param: SpectrumParam):
        """
        Gets a device readings using a GET request to the Spectrum API.

        Parameters
        ----------
        param: SpectrumParam
            SpectrumParam object that contains Spectrum API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'apikey': param.apikey,
            'start_date_org': param.start_date_org,
            'start_date': param.start_date,
            'end_date_org': param.end_date_org,
            'end_date': param.end_date,
            'date_org': param.date_org,
            'date': param.date,
            'conversion_msg': param.conversion_msg,
            'count': param.count,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__parse()
        elif param.sn and param.apikey:
            self.__get(param.sn, param.apikey, param.start_date, param.end_date, param.date, param.count)
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

    def __get(self, sn, apikey, start_date=None, end_date=None, date=None, count=None):
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
        self.__build(sn, apikey, start_date, end_date, date, count)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, sn, apikey, start_date=None, end_date=None, date=None, count=None):
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

        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Spectrum API and stores the response.
        """
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        if resp.status_code != 200:
            raise Exception(
                'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
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
        #     map(lambda x: SpectrumTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
