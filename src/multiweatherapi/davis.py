import collections
import hashlib
import hmac
import json
from datetime import datetime, timezone
from requests import Session, Request


class DavisParam:
    """
    A class used to represent Davis API parameters
    Attributes
    ----------
    sn : str
        The serial number of the device
    apikey : str
        The customer's access key (v2)
    apisec : str
        API security that is used to compute the hash
    start_date_org : datetime
        Stores datetime object passed initially
    start_date : datetime (UTC expected)
        Return readings with timestamps ≥ start_time. Specify start_time in str. (2021-08-01, 2021-08-01)
    end_date_org : datetime
        Stores datetime object passed initially
    end_date : datetime (UTC expected)
        Return readings with timestamps ≤ end_time. Specify end_time in str. (2021-08-31, 2021-08-31)
    conversion_msg : str
        Stores time conversion message
    json_file : str, optional
        The path to a local json file to parse
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, apikey=None, apisec=None, start_date=None, end_date=None, json_file=None,
                 binding_ver=None):
        self.sn = sn
        self.apikey = apikey
        self.apisec = apisec
        self.apisig = None
        self.t = int(datetime.now().timestamp())
        # self.start_date = int(time.mktime(time.strptime(start_date, "%m/%d/%Y %H:%M"))) if start_date else None
        # self.end_date = int(time.mktime(time.strptime(end_date, "%m/%d/%Y %H:%M"))) if end_date else None
        self.start_date_org = start_date
        self.start_date = start_date
        self.end_date_org = end_date
        self.end_date = end_date
        self.conversion_msg = ''
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()

        if json_file is None:
            self.__compute_signature()

    def __check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise Exception('start_date must be earlier than end_date')
        if self.apikey is None or self.apisec is None:
            raise Exception('"apikey" and "apisec" parameters must both be included.')
        if self.sn is None:
            raise Exception('"sn" parameter must be included.')

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
        self.start_date = int(self.start_date.timestamp()) if self.start_date else None
        self.end_date = int(self.end_date.timestamp()) if self.end_date else None

    def __compute_signature(self):
        params = {
            'api-key': self.apikey,
            'station-id': self.sn,
            't': self.t
        }
        if self.start_date and self.end_date:
            params['start-timestamp'] = self.start_date
            params['end-timestamp'] = self.end_date

        params = collections.OrderedDict(sorted(params.items()))
        for key in params:
            print("Parameter name: \"{}\" has value \"{}\"".format(key, params[key]))

        data = ""
        for key in params:
            data = data + key + str(params[key])
        print("Data string to hash is: \"{}\"".format(data))

        self.apisig = hmac.new(
            self.apisec.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        print("API Signature is: \"{}\"".format(self.apisig))


class DavisReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Davis server
    response : Response
        a json response from the Davis server
    parsed_resp : list of dict
        a parsed response from
    debug_info : dict
        a dict structure consist of parameter name and values
    """
    def __init__(self, param: DavisParam):
        """
        Gets a device readings using a GET request to the Davis API.
        Parameters
        ----------
        param : DavisParam
            DavisParam object that contains Davis API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'apikey': param.apikey,
            'apisig': param.apisig,
            't': param.t,
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
        elif param.sn and param.apikey:
            self.__get(param.sn, param.apikey, param.apisig, param.t, param.start_date, param.end_date)
        elif param.sn or param.apikey:
            raise Exception('"sn" and "apikey" parameters must both be included.')
        else:
            # build an empty DavisToken
            self.request = None
            self.response = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, sn, apikey, apisig, t, start_date=None, end_date=None):
        """
        Gets a device readings using a GET request to the Davis API.
        Wraps build and parse functions.
        Parameters
        ----------
        sn : str
            The serial number of the device
        apikey : str
            The user's API access key
        apisig : str
            API signature calculated when parameter object is instantiated
        t : int
            Unix timestamp when the query is submitted
        start_date : int, optional
            Return readings with timestamps ≥ start_date.
        end_date : int, optional
            Return readings with timestamps ≤ end_date.
        """
        self.__build(sn, apikey, apisig, t, start_date, end_date)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, sn, apikey, apisig, t, start_date=None, end_date=None):
        """
        Gets a device readings using a GET request to the Davis API.
        Parameters
        ----------
        sn : str
            The serial number of the device
        apikey : str
            The user's API access key
        apisig : str
            API signature calculated when parameter object is instantiated
        t : int
            Unix timestamp when the query is submitted
        start_date : int, optional
            Return readings with timestamps ≥ start_date.
        end_date : int, optional
            Return readings with timestamps ≤ end_date.
        """
        if start_date and end_date:
            self.request = Request('GET',
                                   url='https://api.weatherlink.com/v2/historic/' + sn,
                                   params={'api-key': apikey,
                                           't': t,
                                           'start-timestamp': start_date,
                                           'end-timestamp': end_date,
                                           'api-signature': apisig}).prepare()
        else:
            self.request = Request('GET',
                                   url='https://api.weatherlink.com/v2/current/' + sn,
                                   params={'api-key': apikey,
                                           't': t,
                                           'api-signature': apisig}).prepare()

        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Davis API and stores the response.
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
        #     map(lambda x: DavisTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
