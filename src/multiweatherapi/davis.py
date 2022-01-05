import collections
import hashlib
import hmac
import json
from datetime import datetime
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
    start_date : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in str. (2021-08-01, 2021-08-01)
    end_date : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in str. (2021-08-31, 2021-08-31)
    json_file : str, optional
        The path to a local json file to parse.
    """
    def __init__(self, sn=None, apikey=None, apisec=None, start_date=None, end_date=None, json_file=None):
        self.sn = sn
        self.apikey = apikey
        self.apisec = apisec
        self.apisig = None
        self.t = int(datetime.now().timestamp())
        # self.start_date = int(time.mktime(time.strptime(start_date, "%m/%d/%Y %H:%M"))) if start_date else None
        # self.end_date = int(time.mktime(time.strptime(end_date, "%m/%d/%Y %H:%M"))) if end_date else None
        self.start_date = start_date
        self.end_date = end_date
        self.json_file = json_file

        self.check_params()
        self.format_time()

        if json_file is None:
            self.compute_signature()

    def format_time(self):
        self.start_date = int(self.start_date.timestamp()) if self.start_date else None
        self.end_date = int(self.end_date.timestamp()) if self.end_date else None

    def check_params(self):
        if self.start_date and not isinstance(self.start_date, datetime):
            raise Exception('start_date must be datetime.datetime instance')
        if self.end_date and not isinstance(self.end_date, datetime):
            raise Exception('end_date must be datetime.datetime instance')
        if self.apikey is None or self.apisec is None:
            raise Exception('"apikey" and "apisec" parameters must both be included.')
        if self.sn is None:
            raise Exception('"sn" parameter must be included.')

    def compute_signature(self):
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
    """
    def __init__(self, param: DavisParam):
        """
        Gets a device readings using a GET request to the Davis API.
        Parameters
        ----------
        param : DavisParam
            DavisParam object that contains Davis API parameters
        """
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.parse()
        elif param.sn and param.apikey:
            self.get(param.sn, param.apikey, param.apisig, param.t, param.start_date, param.end_date)
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

    def get(self, sn, apikey, apisig, t, start_date=None, end_date=None):
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
        self.build(sn, apikey, apisig, t, start_date, end_date)
        self.make_request()
        self.parse()
        return self

    def build(self, sn, apikey, apisig, t, start_date=None, end_date=None):
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
        return self

    def make_request(self):
        """
        Sends a token request to the Davis API and stores the response.
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
        #     map(lambda x: DavisTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
