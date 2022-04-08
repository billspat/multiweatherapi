import collections
import hashlib
import hmac
import json
from datetime import datetime, timezone, timedelta
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
    start_datetime : datetime (UTC expected)
        Return readings with timestamps ≥ start_time. Specify start_time in str. (2021-08-01, 2021-08-01)
    end_datetime : datetime (UTC expected)
        Return readings with timestamps ≤ end_time. Specify end_time in str. (2021-08-31, 2021-08-31)
    date_tuple_list : list
        A list of date/time tuples with API signatures
    conversion_msg : str
        Stores time conversion message
    json_file : str, optional
        The path to a local json file to parse
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, apikey=None, apisec=None, start_datetime=None, end_datetime=None, json_file=None,
                 binding_ver=None):
        self.sn = sn
        self.apikey = apikey
        self.apisec = apisec
        self.apisig = None  # used when start_datetime & end_datetime is passed
        self.t = int(datetime.now().timestamp())
        # self.start_datetime = int(time.mktime(time.strptime(start_datetime, "%m/%d/%Y %H:%M")))
        # if start_datetime else None
        # self.end_datetime = int(time.mktime(time.strptime(end_datetime, "%m/%d/%Y %H:%M"))) if end_datetime else None
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.date_tuple_list = list()
        self.conversion_msg = ''
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()

        if json_file is None:
            self.__compute_signature()

    def __check_params(self):
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if self.apikey is None or self.apisec is None:
            raise Exception('"apikey" and "apisec" parameters must both be included.')
        if self.sn is None:
            raise Exception('"sn" parameter must be included.')

        if self.start_datetime and self.end_datetime:
            if self.end_datetime - timedelta(hours=24) < self.start_datetime:
                self.date_tuple_list.append((self.start_datetime, self.end_datetime))
            else:
                while self.end_datetime - timedelta(hours=24) >= self.start_datetime:
                    self.date_tuple_list.append(
                        (self.start_datetime, self.start_datetime + timedelta(hours=23, minutes=59, seconds=59)))
                    self.start_datetime += timedelta(hours=24)
                self.date_tuple_list.append((self.start_datetime, self.end_datetime))
            for elem in self.date_tuple_list:
                print(elem)

    def __utc_to_local(self):
        # this method does not affect the API outcome at all may be removed without any issue
        print('UTC Start date: {}'.format(self.start_datetime))
        # self.conversion_msg += 'UTC start date passed as parameter: {}'.format(self.start_datetime) + " \\ "
        self.conversion_msg += 'Davis utilizes Unix Epoch, just added explicit UTC timezone' + " \\ "
        # self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        # if self.start_datetime else None
        self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc) if self.start_datetime else None
        print('Explicit UTC time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Explicit UTC time start date after conversion: {}'.format(self.start_datetime) + " \\ "
        #
        print('UTC End date: {}'.format(self.end_datetime))
        self.conversion_msg += 'UTC end date passed as parameter: {}'.format(self.end_datetime) + " \\ "
        # # self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        # if self.end_datetime else None
        self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc) if self.end_datetime else None
        self.conversion_msg += 'Explicit UTC time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        print('Explicit UTC time End date: {}'.format(self.end_datetime))

    def __format_time(self):
        self.__utc_to_local()
        # self.start_datetime = int(self.start_datetime.timestamp()) if self.start_datetime else None
        # self.end_datetime = int(self.end_datetime.timestamp()) if self.end_datetime else None
        if self.start_datetime and self.end_datetime:
            temp_list = list()
            for st, ed in self.date_tuple_list:
                st = int(st.replace(tzinfo=timezone.utc).timestamp())
                ed = int(ed.replace(tzinfo=timezone.utc).timestamp())
                temp_list.append((st, ed))
            self.date_tuple_list = temp_list

    def __compute_signature(self):

        def compute_signature_engine():  # compute_engine
            for key in params:
                print("Parameter name: \"{}\" has value \"{}\"".format(key, params[key]))

            data = ""
            for key in params:
                data = data + key + str(params[key])
            print("Data string to hash is: \"{}\"".format(data))

            sig = hmac.new(
                self.apisec.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256).hexdigest()
            print("API Signature is: \"{}\"".format(sig))
            return sig

        if self.start_datetime and self.end_datetime:
            temp_list = list()
            for st, ed in self.date_tuple_list:
                params = {'api-key': self.apikey,
                          'station-id': self.sn,
                          't': self.t,
                          'start-timestamp': st,
                          'end-timestamp': ed}
                params = collections.OrderedDict(sorted(params.items()))
                apisig = compute_signature_engine()
                temp_list.append((st, ed, apisig))
            self.date_tuple_list = temp_list
            for elem in self.date_tuple_list:
                print(elem)
        else:
            params = {'api-key': self.apikey, 'station-id': self.sn, 't': self.t}
            params = collections.OrderedDict(sorted(params.items()))
            self.apisig = compute_signature_engine()


class DavisReadings:
    """
    A class used to represent a device's readings
    Attributes
    ----------
    requests : list
        a list of Request objects defining the request made to the Davis server
    responses : list
        a (combined) raw json responses from the Davis server
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
            't': param.t,
            'apisig': param.apisig,
            'date_tuple_list': param.date_tuple_list,
            'conversion_msg': param.conversion_msg,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        self.requests = list()
        self.responses = list()

        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__parse()
        elif param.sn and param.apikey:
            self.__get(param.sn, param.apikey, param.apisig, param.date_tuple_list, param.t)
        elif param.sn or param.apikey:
            raise Exception('"sn" and "apikey" parameters must both be included.')
        else:
            # build an empty DavisToken
            self.requests = None
            self.responses = None
            self.parsed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, sn, apikey, apisig, date_tuple_list, t):
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
        date_tuple_list : list
            A list of date/time tuples with API signatures
        t : int
            Unix timestamp when the query is submitted
        """
        self.__build(sn, apikey, apisig, date_tuple_list, t)
        self.__make_request()
        self.__parse()
        return self

    def __build(self, sn, apikey, apisig, date_tuple_list, t):
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
        date_tuple_list : list
            A list of date/time tuples with API signatures
        t : int
            Unix timestamp when the query is submitted
        """
        if len(date_tuple_list) != 0:
            for st, ed, sig in date_tuple_list:
                tmp_request = Request('GET',
                                      url='https://api.weatherlink.com/v2/historic/' + sn,
                                      params={'api-key': apikey,
                                              't': t,
                                              'start-timestamp': st,
                                              'end-timestamp': ed,
                                              'api-signature': sig}).prepare()
                self.requests.append(tmp_request)
        else:
            tmp_request = Request('GET',
                                  url='https://api.weatherlink.com/v2/current/' + sn,
                                  params={'api-key': apikey, 't': t, 'api-signature': apisig}).prepare()
            self.requests.append(tmp_request)

        self.debug_info['requests'] = self.requests
        # self.debug_info['http_method'] = self.request.method
        # self.debug_info['url'] = self.request.url
        # self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Davis API and stores the response.
        """
        # Send the request and get the JSON response
        for req in self.requests:
            resp = Session().send(req)
            if resp.status_code != 200:
                raise Exception(
                    'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
            self.responses.append(resp.json())
            # self.debug_info['response'] = self.response

        self.responses.append({'python_binding_version': self.debug_info['binding_ver']})
        return self

    def __parse(self):
        """
        Parses the response.
        """
        self.parsed_resp = list()
        # try:
        #     self.device_info = self.response['device']['device_info']
        # except KeyError:
        #     self.device_info = 'N/A'
        # self.timeseries = list(
        #     map(lambda x: DavisTimeseriesRecord(x), self.response['device']['timeseries']))
        return self
