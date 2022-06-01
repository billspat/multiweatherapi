import collections
import hashlib
import hmac
import json
import pytz
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
    def __init__(self, sn=None, apikey=None, apisec=None, start_datetime=None, end_datetime=None, tz=None,
                 json_file=None, binding_ver=None):
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
        self.cur_datetime = datetime.now(timezone.utc)
        self.tz = tz
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
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('state_datetime and end_datetime must be specified')
        if self.apikey is None or self.apisec is None:
            raise Exception('"apikey" and "apisec" parameters must both be included.')
        if self.sn is None:
            raise Exception('"sn" parameter must be included.')

        if self.start_datetime and self.end_datetime:
            # remove sub-second since API cannot distinguish them different
            self.start_datetime = self.start_datetime.replace(microsecond=0)
            self.end_datetime = self.end_datetime.replace(microsecond=0)
            if self.end_datetime - timedelta(hours=24) <= self.start_datetime:
                self.date_tuple_list.append((self.start_datetime, self.end_datetime))
            else:
                while self.end_datetime - timedelta(hours=24) > self.start_datetime:
                    self.date_tuple_list.append(
                        (self.start_datetime, self.start_datetime + timedelta(hours=23, minutes=59, seconds=59)))
                    self.start_datetime += timedelta(hours=24)
                self.date_tuple_list.append((self.start_datetime, self.end_datetime))
            for elem in self.date_tuple_list:
                print(elem)

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
        self.conversion_msg += 'Davis utilizes Unix Epoch, this routine is used for metadata purposes' + " \\ "
        self.conversion_msg += \
            'UTC start date passed as parameter: {}, local time zone: {}'.format(self.start_datetime, self.tz) + " \\ "
        self.start_datetime = None if not self.start_datetime else \
            self.start_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        print('Local time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Local time start date after conversion: {}'.format(self.start_datetime) + " \\ "

        print('UTC End date: {}, local time zone: {}'.format(self.end_datetime, self.tz))
        self.conversion_msg += \
            'UTC end date passed as parameter: {}, local time zone: {}'.format(self.end_datetime, self.tz) + " \\ "
        self.end_datetime = None if not self.end_datetime else \
            self.end_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        print('Local time End date: {}'.format(self.end_datetime))
        self.conversion_msg += 'Local time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        self.cur_datetime = self.cur_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))

    def __format_time(self):
        # this part is for the metadata purposes
        self.__utc_to_local()
        self.start_datetime = self.start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.start_datetime else None
        self.end_datetime = self.end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.end_datetime else None
        self.cur_datetime = self.cur_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # this part is for actual API call
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
    request : list
        a list of Request objects defining the request made to the Davis server
    response : list
        a (combined) raw json responses from the Davis server
    transformed_resp : list of dict
        a transformed response from raw JSON file or raw JSON response
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
            'start_datetime': param.start_datetime,
            'end_datetime': param.end_datetime,
            'cur_datetime': param.cur_datetime,
            'tz': param.tz,
            'conversion_msg': param.conversion_msg,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        self.request = list()
        self.response = list()

        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__transform()
        elif param.sn and param.apikey:
            self.__get(param.sn, param.apikey, param.apisig, param.date_tuple_list, param.t)
        elif param.sn or param.apikey:
            raise Exception('"sn" and "apikey" parameters must both be included.')
        else:
            # build an empty DavisToken
            self.request = None
            self.response = None
            self.transformed_resp = None
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
        self.__transform()
        return self

    def __build(self, sn, apikey, apisig, date_tuple_list: list, t):
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
                self.request.append(tmp_request)
        else:
            tmp_request = Request('GET',
                                  url='https://api.weatherlink.com/v2/current/' + sn,
                                  params={'api-key': apikey, 't': t, 'api-signature': apisig}).prepare()
            self.request.append(tmp_request)

        self.debug_info['request'] = self.request
        # self.debug_info['http_method'] = self.request.method
        # self.debug_info['url'] = self.request.url
        # self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Davis API and stores the response.
        """
        # prep response list
        metadata = {
            "vendor": "davis",
            "station_id": self.debug_info['sn'],
            "timezone": self.debug_info['tz'],
            "start_datetime": self.debug_info['start_datetime'],
            "end_datetime": self.debug_info['end_datetime'],
            "request_time": self.debug_info['cur_datetime'],
            "python_binding_version": self.debug_info['binding_ver']}
        self.response.append(metadata)
        # Send the request and get the JSON response
        for req in self.request:
            resp = Session().send(req)
            if resp.status_code != 200:
                raise Exception(
                    'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
            self.response.append(resp.json())
            # self.debug_info['response'] = self.response
        return self

    def __transform(self):
        """
        Transform the response.
        """
        def epoch_converter(epoch, time_zone):
            tzlist = {
                'HT': 'US/Hawaii',
                'AT': 'US/Alaska',
                'PT': 'US/Pacific',
                'MT': 'US/Mountain',
                'CT': 'US/Central',
                'ET': 'US/Eastern'
            }
            utc_dt = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
            tz = pytz.timezone(tzlist[time_zone])
            dt = utc_dt.astimezone(tz)
            return dt.strftime('%Y-%m-%d %H:%M:%S')

        self.transformed_resp = list()
        station_id = self.response[0]['station_id']
        request_datetime = self.response[0]['request_time']
        for idx in range(1, len(self.response)):
            sensors = self.response[idx]['sensors']
            for jdx in range(len(sensors)):
                data = sensors[jdx]['data']
                for kdx in range(len(data)):
                    if "temp_out" not in data[kdx]:
                        break
                    else:
                        temp_dic = {
                            "station_id": station_id,
                            "request_datetime": request_datetime,
                            "data_datetime": epoch_converter(data[kdx]['ts'], self.response[0]['timezone']),
                            "atemp": round(((float(data[kdx]['temp_out']) - 32) * 5 / 9), 1),
                            "pcpn": data[kdx]['rainfall_mm'],
                            "relh": data[kdx]['hum_out']
                        }
                        self.transformed_resp.append(temp_dic)
        print(self.transformed_resp)
        return self
