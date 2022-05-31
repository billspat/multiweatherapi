from datetime import datetime, timezone
import json
import pytz
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
    start_datetime_org : datetime
        Stores datetime object passed initially
    start_datetime : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_datetime_org : datetime
        Stores datetime object passed initially
    end_datetime : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    conversion_msg : str
        Stores time conversion message
    sensor_sn : dict
        a dict of sensor serial numbers
    json_file : str, optional
        The path to a local json file to parse.
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, client_id=None, client_secret=None, ret_form=None, user_id=None, start_datetime=None,
                 end_datetime=None, tz=None, sensor_sn=None, json_file=None, binding_ver=None):
        self.sn = sn
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.ret_form = ret_form
        self.user_id = user_id
        self.path_param = None
        self.start_datetime_org = start_datetime
        self.start_datetime = start_datetime
        self.end_datetime_org = end_datetime
        self.end_datetime = end_datetime
        self.cur_datetime = datetime.now(timezone.utc)
        self.tz = tz
        self.conversion_msg = ''
        self.sensor_sn_dict = sensor_sn
        self.json_file = json_file
        self.binding_ver = binding_ver

        self.__check_params()
        self.__format_time()
        self.__get_auth()

    def __check_params(self):
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('state_datetime and end_datetime must be specified')
        if self.client_id is None or self.client_secret is None:
            raise Exception('client_id and client_secret parameters must be included')
        if self.ret_form is None or self.ret_form != 'JSON':
            raise Exception('ret_form must be specified and currently only \'JSON\' is supported')
        if self.user_id is None or not isinstance(self.user_id, str):
            raise Exception('userId must be specified and only str type is supported')
        self.path_param = {'format': self.ret_form, 'userId': self.user_id}

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
        self.conversion_msg += 'UTC start date passed as parameter: {}'.format(self.start_datetime) + " \\ "
        self.conversion_msg += 'Onset utilizes UTC timestamp as is, just added explicit UTC timezone' + " \\ "
        # self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None) \
        #     if self.start_datetime else None
        self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc) if self.start_datetime else None
        print('Explicit UTC time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Explicit UTC time start date after conversion: {}'.format(self.start_datetime) + " \\ "

        print('UTC End date: {}'.format(self.end_datetime))
        self.conversion_msg += 'UTC end date passed as parameter: {}'.format(self.end_datetime) + " \\ "
        # self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        # if self.end_datetime else None
        self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc) if self.end_datetime else None
        self.conversion_msg += 'Explicit UTC time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        print('Explicit UTC time End date: {}'.format(self.end_datetime))
        # for the metadata
        self.start_datetime_org = \
            self.start_datetime_org.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        self.end_datetime_org = \
            self.end_datetime_org.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))
        self.cur_datetime = self.cur_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))

    def __format_time(self):
        self.__utc_to_local()
        # self.start_datetime = self.start_datetime.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        # if self.start_datetime \
        self.start_datetime = self.start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.start_datetime \
            else datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.end_datetime = self.end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.end_datetime \
            else datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        # for metadata
        self.start_datetime_org = self.start_datetime_org.strftime('%Y-%m-%d %H:%M:%S')
        self.end_datetime_org = self.end_datetime_org.strftime('%Y-%m-%d %H:%M:%S')
        self.cur_datetime = self.cur_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def __get_auth(self):
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
        a raw json response from the Onset server combined with meta data
    transformed_resp : list of dict
        a transformed response from raw JSON file or raw JSON response
    debug_info : dict
        a dict structure consist of parameter name and values
    """

    def __init__(self, param: OnsetParam):
        """
        Gets a device readings using a GET request to the Onset API.
        Parameters
        ----------
        param : OnsetParam
            OnsetParam object that contains Onset API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'access_token': param.access_token,
            'path_param': param.path_param,
            'start_datetime_org': param.start_datetime_org,
            'start_datetime': param.start_datetime,
            'end_datetime_org': param.end_datetime_org,
            'end_datetime': param.end_datetime,
            'cur_datetime': param.cur_datetime,
            'tz': param.tz,
            'conversion_msg': param.conversion_msg,
            'sensor_sn': param.sensor_sn_dict,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__transform()
        elif param.sn and param.access_token:
            self.__get(param.sn, param.access_token, param.path_param, param.start_datetime, param.end_datetime)
        elif param.sn or param.access_token:
            raise Exception('"sn" and "access_token" parameters must both be included.')
        else:
            # build an empty OnsetToken
            self.request = None
            self.response = None
            self.transformed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, sn, access_token, path_param, start_datetime, end_datetime):
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
        start_datetime : str
            Return readings with timestamps ≥ start_datetime.
        end_datetime : str
            Return readings with timestamps ≤ end_datetime.
        """
        self.__build(sn, access_token, path_param, start_datetime, end_datetime)
        self.__make_request()
        self.__transform()
        return self

    def __build(self, sn, access_token, path_param, start_datetime, end_datetime):
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
        start_datetime : str
            Return readings with timestamps ≥ start_datetime.
        end_datetime : str
            Return readings with timestamps ≤ end_datetime.
        """
        self.request = Request('GET',
                               url='https://webservice.hobolink.com/ws/data/file/{format}/user/{userId}'.format(
                                   **path_param),
                               headers={
                                   'Authorization': "Bearer " + access_token},
                               params={'loggers': sn,
                                       'start_date_time': start_datetime,
                                       'end_date_time': end_datetime}).prepare()
        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Onset API and stores the response.
        """
        # prep response list
        self.response = list()
        metadata = {
            "vendor": "onset",
            "station_id": self.debug_info['sn'],
            "timezone": self.debug_info['tz'],
            "start_datetime": self.debug_info['start_datetime_org'],
            "end_datetime": self.debug_info['end_datetime_org'],
            "request_time": self.debug_info['cur_datetime'],
            "python_binding_version": self.debug_info['binding_ver']}
        self.response.append(metadata)
        # Send the request and get the JSON response
        resp = Session().send(self.request)
        if resp.status_code != 200:
            raise Exception(
                'Request failed with \'{}\' status code and \'{}\' message.'.format(resp.status_code, resp.text))
        elif str(resp.content) == str(b'{"Error": "Device serial number entered does not exist"}'):
            raise Exception(
                'Error: Device serial number entered does not exist')
        self.response.append(resp.json())
        self.debug_info['response'] = self.response
        return self

    def __transform(self):
        """
        Parses the response.
        """
        def search_timestamp(input_datetime):
            if self.transformed_resp is None:
                return None
            if len(self.transformed_resp) == 0:
                return -1
            for x in range(len(self.transformed_resp)):
                if input_datetime == self.transformed_resp[x]['data_datetime']:
                    return x
            return -1

        def insert_resp(key, value, rec_datetime):
            resp_index = search_timestamp(rec_datetime)
            if resp_index is None:
                raise Exception("transformed_resp is None")
            elif resp_index == -1:
                temp_dict = {
                    "station_id": station_id,
                    "request_datetime": request_datetime,
                    "data_datetime": data_datetime,
                    key: value
                }
                self.transformed_resp.append(temp_dict)
            else:
                self.transformed_resp[resp_index][key] = value

        self.transformed_resp = list()
        station_id = self.response[0]['station_id']
        request_datetime = self.response[0]['request_time']
        for idx in range(1, len(self.response)):
            observe_list = self.response[idx]['observation_list']
            for kdx in range(len(observe_list)):
                if self.debug_info['sensor_sn']['atemp'] == observe_list[kdx]['sensor_sn']:
                    data_datetime = observe_list[kdx]['timestamp']
                    atemp = round(float(observe_list[kdx]['si_value']), 1)
                    insert_resp("atemp", atemp, data_datetime)

                if self.debug_info['sensor_sn']['pcpn'] == observe_list[kdx]['sensor_sn']:
                    data_datetime = observe_list[kdx]['timestamp']
                    pcpn = observe_list[kdx]['si_value']
                    insert_resp("pcpn", pcpn, data_datetime)

                if self.debug_info['sensor_sn']['relh'] == observe_list[kdx]['sensor_sn']:
                    data_datetime = observe_list[kdx]['timestamp']
                    relh = observe_list[kdx]['us_value']
                    insert_resp("relh", relh, data_datetime)

        print(self.transformed_resp)
        return self
