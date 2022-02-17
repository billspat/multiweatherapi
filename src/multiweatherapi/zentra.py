from datetime import datetime, timezone
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
    start_date_org : datetime
        Stores datetime object passed initially
    start_date : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_date_org : datetime
        Stores datetime object passed initially
    end_date : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    conversion_msg : str
        Stores time conversion message
    start_mrid : int, optional
        Return readings with mrid ≥ start_mrid.
    end_mrid : int, optional
        Return readings with mrid ≤ start_mrid.
    json_file : str, optional
        The path to a local json file to parse.
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, token=None, start_date=None, end_date=None, start_mrid=None, end_mrid=None,
                 json_file=None, binding_ver=None):
        self.sn = sn
        self.token = token
        self.start_date_org = start_date
        self.start_date = start_date
        self.end_date_org = end_date
        self.end_date = end_date
        self.conversion_msg = ''
        self.start_mrid = start_mrid
        self.end_mrid = end_mrid
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

    def __utc_to_local(self):
        print('UTC Start date: {}'.format(self.start_date))
        self.conversion_msg += 'UTC start date passed as parameter: {}'.format(self.start_date) + " \\ "
        self.start_date = self.start_date.replace(tzinfo=timezone.utc).astimezone(tz=None) if self.start_date else None
        print('Local time Start date: {}'.format(self.start_date))
        self.conversion_msg += 'Local time start date after conversion: {}'.format(self.start_date) + " \\ "

        print('UTC End date: {}'.format(self.end_date))
        self.conversion_msg += 'UTC end date passed as parameter: {}'.format(self.end_date) + " \\ "
        self.end_date = self.end_date.replace(tzinfo=timezone.utc).astimezone(tz=None) if self.end_date else None
        self.conversion_msg += 'Local time end date after conversion: {}'.format(self.end_date) + " \\ "
        print('Local time End date: {}'.format(self.end_date))

    def __format_time(self):
        self.__utc_to_local()
        self.start_date = self.start_date.strftime('%m-%d-%Y %H:%M') if self.start_date \
            else datetime.now().strftime('%m-%d-%Y %H:%M')
        self.end_date = self.end_date.strftime('%m-%d-%Y %H:%M') if self.end_date \
            else datetime.now().strftime('%m-%d-%Y %H:%M')


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
    debug_info : dict
        a dict structure consist of parameter name and values
    """

    def __init__(self, param: ZentraParam):
        """
        Gets a device readings using a GET request to the Zentra API.
        Parameters
        ----------
        param : ZentraParam
            ZentraParam object that contains Zentra API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'token': param.token,
            'start_date_org': param.start_date_org,
            'start_date': param.start_date,
            'end_date_org': param.end_date_org,
            'end_date': param.end_date,
            'conversion_msg': param.conversion_msg,
            'start_mrid': param.start_mrid,
            'end_mrid': param.end_mrid,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__parse()
        elif param.sn and param.token:
            self.__get(param.sn, param.token, param.start_date, param.end_date, param.start_mrid, param.end_mrid)
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

    def __get(self, sn, token, start_date=None, end_date=None, start_mrid=None, end_mrid=None):
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
        self.__build(sn, token, start_date, end_date, start_mrid, end_mrid)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, sn, token, start_date=None, end_date=None, start_mrid=None, end_mrid=None):
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
        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
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
        #     map(lambda x: ZentraTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
