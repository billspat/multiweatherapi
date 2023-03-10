from datetime import datetime, timezone
import json
from time import sleep

import pytz
from requests import Session, Request
from .utilities import Utilities as utilities


class ZentraParam:
    """
    A class used to represent Zentra API parameters

    Attributes
    ----------
    sn : str
        The serial number of the device
    token : str
        The user's access token
    start_datetime : datetime
        Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format
    end_datetime : datetime
        Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format
    conversion_msg : str
        Stores time conversion message
    tz : str
        Time zone information
    start_mrid : int, optional
        Return readings with mrid ≥ start_mrid.
    end_mrid : int, optional
        Return readings with mrid ≤ start_mrid.
    json_file : str, optional
        The path to a local json file to parse.
    binding_ver : str
        Python binding version
    """
    def __init__(self, sn=None, token=None, start_datetime=None, end_datetime=None, tz=None, start_mrid=None,
                 end_mrid=None, json_file=None, binding_ver=None):

        """
        This module initializes a ZentraParam object.

        Parameters
        ----------
        sn : str
            The serial number of the device.
        token : str
            The user's access token.
        start_datetime : datetime
            Return readings with timestamps ≥ start_time. Specify start_time in Python Datetime format.
        end_datetime : datetime
            Return readings with timestamps ≤ end_time. Specify end_time in Python Datetime format.
        tz : str
            Time zone information
        start_mrid : int
            Return readings with mrid ≥ start_mrid.
        end_mrid : int
            Return readings with mrid ≤ start_mrid.
        json_file : str
            The path to a local json file to parse.
        binding_ver : str
            Python binding version.        
        ----------
        """                 
        self.sn = sn
        self.token = token
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.cur_datetime = datetime.now(timezone.utc)
        self.tz = tz
        self.conversion_msg = ''
        self.start_mrid = start_mrid
        self.end_mrid = end_mrid
        self.json_file = json_file
        self.binding_ver = binding_ver

    def _process(self):
        """ 
        This method does the following:
        - Checks to make sure all the parameters are present and are of the correct type.
        - Formats dates to local time.
        """           
        self.__check_params()
        self.__format_time()

    def __check_params(self):
        """
        This module is called by _process and checks that all the parameters that go to the API are present and of the
        correct data type.

        Raises
        ------
        Exception
            If any parameter is missing or of an incorrect data type.
        """

        tz_option = ['HT', 'AT', 'PT', 'MT', 'CT', 'ET']
        if self.start_datetime and not isinstance(self.start_datetime, datetime):
            raise Exception('start_datetime must be datetime.datetime instance')
        if self.end_datetime and not isinstance(self.end_datetime, datetime):
            raise Exception('end_datetime must be datetime.datetime instance')
        if self.start_datetime and self.end_datetime and (self.start_datetime > self.end_datetime):
            raise Exception('start_datetime must be earlier than end_datetime')
        if not self.json_file and not (self.start_datetime and self.end_datetime):
            raise Exception('start_datetime and end_datetime must be specified')
        if self.tz and (self.tz not in tz_option):
            raise Exception('time zone options: HT, AT, PT, MT, CT, ET')
        if (self.start_datetime or self.end_datetime) and not self.tz:
            raise Exception('if start_datetime or end_datetime is specified, tz must be specified')

    def __utc_to_local(self):
        """
        This method converts a datetime object from UTC to the local time zone.
        """

        tzlist = {
            'HT': 'US/Hawaii',
            'AT': 'US/Alaska',
            'PT': 'US/Pacific',
            'MT': 'US/Mountain',
            'CT': 'US/Central',
            'ET': 'US/Eastern'
        }
        print('UTC Start date: {}, local time zone: {}'.format(self.start_datetime, self.tz))
        self.conversion_msg += \
            'UTC start date passed as parameter: {}, local time zone: {}'.format(self.start_datetime, self.tz) + " \\ "
        # self.start_datetime = self.start_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None) \
        #     if self.start_datetime else None
        self.start_datetime = \
            self.start_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz])) \
            if self.start_datetime else None
        print('Local time Start date: {}'.format(self.start_datetime))
        self.conversion_msg += 'Local time start date after conversion: {}'.format(self.start_datetime) + " \\ "

        print('UTC End date: {}, local time zone: {}'.format(self.end_datetime, self.tz))
        self.conversion_msg += \
            'UTC end date passed as parameter: {}, local time zone: {}'.format(self.end_datetime, self.tz) + " \\ "
        self.end_datetime = self.end_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz])) \
            if self.end_datetime else None
        self.conversion_msg += 'Local time end date after conversion: {}'.format(self.end_datetime) + " \\ "
        print('Local time End date: {}'.format(self.end_datetime))
        self.cur_datetime = self.cur_datetime.replace(tzinfo=timezone.utc).astimezone(pytz.timezone(tzlist[self.tz]))

    def __format_time(self):
        """
        This module makes sure that the date is formatted as MM-DD-YYYY.
        """
        self.__utc_to_local()
        self.start_datetime = self.start_datetime.strftime('%m-%d-%Y %H:%M') if self.start_datetime \
            else datetime.now().strftime('%m-%d-%Y %H:%M')
        self.end_datetime = self.end_datetime.strftime('%m-%d-%Y %H:%M') if self.end_datetime \
            else datetime.now().strftime('%m-%d-%Y %H:%M')
        self.cur_datetime = self.cur_datetime.strftime('%Y-%m-%d %H:%M:%S')


class ZentraReadings:
    """
    A class used to represent a device's readings
    
    Attributes
    ----------
    request : Request
        a Request object defining the request made to the Zentra server
    response : list
        a raw json response from the Zentra server combined with meta data
    transformed_resp : list of dict
        a transformed response from raw JSON file or raw JSON response
    debug_info : dict
        a dict structure consist of parameter name and values
    """

    def __init__(self, param: ZentraParam):
        """
        Initializes a ZentraReadings object.

        Parameters
        ----------
        param : ZentraParam
            ZentraParam object that contains Zentra API parameters
        """
        self.debug_info = {
            'sn': param.sn,
            'token': param.token,
            'start_datetime': param.start_datetime,
            'end_datetime': param.end_datetime,
            'cur_datetime': param.cur_datetime,
            'tz': param.tz,
            'conversion_msg': param.conversion_msg,
            'start_mrid': param.start_mrid,
            'end_mrid': param.end_mrid,
            'json_str': param.json_file,
            'binding_ver': param.binding_ver
        }

    def _process(self, param: ZentraParam):
        """ 
        This method does the following:
        - Checks to make sure that the sn and token parameters are both present.
        - If there is a local JSON file to transform, then do so.
        - Gets the readings from the vendor API.

        Parameters
        ----------
        param : ZentraParam
                The parameters that will be passed to the Zentra API.

        Raises
        ------
        Exception
           If the sn or token parameters are missing.
        """        
        if param.json_file:
            self.response = json.load(open(param.json_file))
            self.__transform()
        elif param.sn and param.token:
            self.__get(param.sn, param.token, param.start_datetime, param.end_datetime, param.start_mrid,
                       param.end_mrid)
        elif param.sn or param.token:
            raise Exception('"sn" and "token" parameters must both be included.')
        else:
            # build an empty ZentraToken
            self.request = None
            self.response = None
            self.transformed_resp = None
            # self.device_info = None
            # self.measurement_settings = None
            # self.time_settings = None
            # self.locations = None
            # self.installation_metadata = None

    def __get(self, sn, token, start_datetime=None, end_datetime=None, start_mrid=None, end_mrid=None):
        """
        Gets device readings from the Zentra API via these steps:
        1. Call __build to build the request.
        2. Call __make_request to make the actual API call.
        3. Call __transform to transform the API response into JSON.

        Parameters
        ----------
        sn : str
            The serial number of the device
        token : str
            The user's access token
        start_datetime : int, optional
            Return readings with timestamps ≥ start_datetime.
        end_datetime : int, optional
            Return readings with timestamps ≤ end_datetime.
        start_mrid : int, optional
            Return readings with mrid ≥ start_mrid.
        end_mrid : int, optional
            Return readings with mrid ≤ start_mrid.

        Returns
        -------
        A ZentraReadings object.            
        """
        self.__build(sn, token, start_datetime, end_datetime, start_mrid, end_mrid)
        self.__make_request()
        self.__transform()
        return self

    def __build(self, sn, token, start_datetime=None, end_datetime=None, start_mrid=None, end_mrid=None):
        """
        This method creates the request which will get sent to the API.

        Parameters
        ----------
        sn : str
            The serial number of the device
        token : str
            The user's access token
        start_datetime : int, optional
            Return readings with timestamps ≥ start_datetime.
        end_datetime : int, optional
            Return readings with timestamps ≤ end_datetime.
        start_mrid : int, optional
            Return readings with mrid ≥ start_mrid.
        end_mrid : int, optional
            Return readings with mrid ≤ start_mrid.

        Returns
        -------
        A ZentraReadings object.            
        """
        self.request = Request('GET',
                               url='https://zentracloud.com/api/v3/get_readings',
                               headers={
                                   'Authorization': "Token " + token},
                               params={'device_sn': sn,
                                       'start_date': start_datetime,
                                       'end_date': end_datetime,
                                       'start_mrid': start_mrid,
                                       'end_mrid': end_mrid}).prepare()
        self.debug_info['http_method'] = self.request.method
        self.debug_info['url'] = self.request.url
        self.debug_info['headers'] = self.request.headers
        return self

    def __make_request(self):
        """
        Sends a token request to the Zentra API and stores the response.

        Returns
        -------
        A ZentraReadings object.        
        """
        # prep response list
        self.response = list()
        metadata = {
            "vendor": "zentra",
            "station_id": self.debug_info['sn'],
            "timezone": self.debug_info['tz'],
            "start_datetime": self.debug_info['start_datetime'],
            "end_datetime": self.debug_info['end_datetime'],
            "request_time": self.debug_info['cur_datetime'],
            "python_binding_version": self.debug_info['binding_ver']}
        self.response.append(metadata)
        # Send the request and get the JSON response
        while True:
            resp = Session().send(self.request)
            if resp.status_code != 429:
                break
            print("message: {}".format(resp.text))
            sleep(60)
        
        self.response[0]['error_msg'] = ''

        if resp.status_code != 200:
            import pprint
            self.response[0]['status_code'] = resp.status_code
            self.response[0]['error_msg'] = utilities.case_insensitive_key(json.loads(resp.text), 'detail')
        elif str(resp.content) == str(b'{"Error": "Device serial number entered does not exist"}'):
            self.response[0]['error_msg'] = utilities.case_insensitive_key(json.loads(resp.text), 'detail')
        
        self.response.append(resp.json())
        self.response[0]['status_code'] = resp.status_code
        self.debug_info['response'] = self.response
        return self

    def __transform(self):
        """
        Transform the response into JSON and store it.

        Returns
        -------
        A ZentraReadings object.        
        """
        def get_reading(data_list, list_index):
            if data_list is None:
                return None
            try:
                reading = round(float(data_list[list_index]['value']), 2)
            except IndexError:
                return None
            return reading

        def get_measurement_list(data_list, measure_label):
            """
            Takes a data list (JSON) object and extract measurement list of interest.

            This inner method can be consolidated with get_reading above by checking 2nd element type
            (e.g., if type is string consider it as label and fetch list, else type is integer then fetch value)

            Parameters
            ----------
            data_list       : dict (JSON)
                              The original resp_raw object.
            measure_label   : str
                              Measurement label of interest

            Returns
            -------
            measurement_list : dict (JSON)
                               Returns measurement list of interest.
            """
            if data_list is None:
                return None
            try:
                measure_list = data_list[measure_label][0]['readings']
            except (KeyError, TypeError):
                print('KeyError or TypeError occurred while fetching measurement list for {}'.format(measure_label))
                measure_list = None
            return measure_list

        self.transformed_resp = utilities.init_transformed_resp(
            'zentra',
            utilities.local_to_utc(self.debug_info['start_datetime'], self.debug_info['tz'], '%m-%d-%Y %H:%M'),
            utilities.local_to_utc(self.debug_info['end_datetime'], self.debug_info['tz'], '%m-%d-%Y %H:%M'))

        if self.response[0]['status_code'] == 200:
            station_id = self.response[0]['station_id']
            request_datetime = self.response[0]['request_time']
            resp_tz = self.response[0]['timezone']

            for idx in range(1, len(self.response)):
                try:
                    data = self.response[idx]['data']
                except (KeyError, TypeError):
                    print("KeyError or TypeError occurred check RAW JSON API")
                    self.transformed_resp = list()
                    return self
                temp_readings = get_measurement_list(data, 'Air Temperature')
                prec_readings = get_measurement_list(data, 'Precipitation')
                relh_readings = get_measurement_list(data, 'Relative Humidity')

                for jdx in range(len(temp_readings)):
                    temp_dic = {
                        "station_id": station_id,
                        "request_datetime": request_datetime,
                        "data_datetime": utilities.local_to_utc(temp_readings[jdx]['datetime'][:-6],
                                                                resp_tz).strftime('%Y-%m-%d %H:%M:%S'),
                        "atemp": get_reading(temp_readings, jdx),
                        "pcpn": get_reading(prec_readings, jdx),
                        "relh": get_reading(relh_readings, jdx),
                    }
                    self.transformed_resp = utilities.insert_resp(self.transformed_resp, temp_dic)
        # print(self.transformed_resp)
        return self
