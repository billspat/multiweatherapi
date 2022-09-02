from datetime import datetime, timedelta
import pytz


class Utilities:
    """
    A class of helper utilities to reduce replication of code across the multiweatherapi modules.
    """

    def case_insensitive_key(this_dict, this_key):
        """
        A class to look for keys in a dictionary, disregarding case.  

        This method is used to look for a particular key in the response string returned by the vendor API call.  Some vendors use 'Message',
        and others use 'message'. 

        Parameters
        ----------
        this_dict : dict
                    The dictionary containing the response from the vendor API.
        this_key  : str
                    They key we are looking for in the response.

        Returns
        -------
        resp_raw : str
                   The value associated with this_key.
        """        
        this_key = this_key.lower()
        value = [this_dict[key] for key in this_dict if key.lower() == this_key][0]
        return value.replace('"', '')
        
    def create_error_response(vendor, parms, readings, error_msg):
        """
        Create an error response that will get placed in the resp_raw field.

        This method came about because it was decided that the raw_data table can double as a log of sorts.  Therefore, it
        was necessary to change how mwapi handled exceptions.  Instead of throwing an exception, mwapi will call this method to create a
        list that can be placed in the resp_raw attribute of the vendor class.  This is mostly for troubleshooting if there was a problem 
        with either the passed parameters or the API call itself.

        Parameters
        ----------
        vendor     : str
                     The name of the vendor.
        parms      : vendor parameter object
                     The parameters that were passed to the vendor API.
        readings   : vendor readings object
                     The readings that were returned by the vendor API (if any). 
        error_msg  : str
                     The error message to place into resp_raw.

        Returns
        -------
        return_list : list
                      A list of items that would have been returned if the API call was successful.  
        """

        temp = {}

        temp['vendor'] = vendor

        if vendor == 'DAVIS' or vendor == 'ONSET' or vendor == 'SPECTRUM'  or vendor == 'ZENTRA':
            temp['station_id'] = readings.debug_info['station_id'] if 'station_id' in readings.debug_info else parms.sn
        elif vendor == 'RAINWISE':
            temp['station_id'] = readings.debug_info['station_id'] if 'station_id' in readings.debug_info else parms.mac
        else:
            temp['station_id'] = readings.debug_info['station_id'] if 'station_id' in readings.debug_info else parms.station_id

        temp['timezone'] = readings.debug_info['tz']
        Utilities.set_date(readings.debug_info['start_datetime'])
        temp['start_datetime'] = Utilities.set_date(readings.debug_info['start_datetime'])
        temp['end_datetime'] = Utilities.set_date(readings.debug_info['end_datetime'])
        temp['request_time'] = Utilities.set_date(readings.debug_info['cur_datetime'])
        temp['python_binding_version'] = readings.debug_info['binding_ver']
        temp['error_msg'] = 'Bad Request: ' + error_msg
        temp['status_code'] = '400'
        temp['api_output'] = []

        return_list = []
        return_list.append(temp)

        return return_list

    def convert_to_dict(resp_raw, davisParm = None):
        """ 
        Takes a resp_raw list object and converts it to a straight dictionary. 

        The resp_raw object starts off as a list, but it needs to be converted to a dictionary before it is written to the raw_data table.
        If this is a Davis station, we need to go through all the resp_raw items as each item in resp_raw is a new 24-hour slice of data.
        This is because Davis stations can only return 24 hours worth of data at a time, so it is called multiple times if we are pulling
        more than a day's worth of data.

        Parameters
        ----------
        resp_raw  : list
                    The original resp_raw object.
        davisParm : DavisParam, optional
                    If present, these are the parameters used to call the Davis API.

        Returns
        ------- 
        new_raw : dict
                  The resp_raw object as a dictionary, with the information from the API call placed in the 'api_output' entry.
        
        """

        new_raw = {}
        new_raw = resp_raw[0]

        if davisParm and davisParm.date_tuple_list:
            end = len(davisParm.date_tuple_list) - 1
            new_raw['start_datetime'] = datetime.fromtimestamp(davisParm.date_tuple_list[0][0], pytz.timezone('America/Detroit')).strftime('%Y-%m-%d %H:%M:%S')
            new_raw['end_datetime'] = datetime.fromtimestamp(davisParm.date_tuple_list[end][1], pytz.timezone('America/Detroit')).strftime('%Y-%m-%d %H:%M:%S')

        # Loop through the resp_raw items, starting with index 1.  If this is a Davis station, there could be multiple items.  
        # Append each item to a temporary dictionary.
        temp = list()
        for i in range(1, len(resp_raw)):
            temp.append(resp_raw[i])
        
        # Set the api_output dictionary element to the temporary list.
        new_raw['api_output'] = temp

        return new_raw

    def set_date(date):
        """
        This method will try to format the date that was sent to it.  If the date sent is invalid, return that so it will go into the
        error log correctly.

        Parameters
        ----------
        date : str or datetime
               The date to be set.
              
        Returns
        -------
        date : str
               The properly formatted date if the date is a proper date, the original value otherwise.      
        """
        from dateutil.parser import parse, ParserError

        if isinstance(date, str):
            try:
                date = parse(date)
                date = date.strftime('%Y-%m-%d %H:%M:%S')
            except ParserError:
                date = date
        elif isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d %H:%M:%S')

        return date

    def local_to_utc(input_datetime_str: str, local_timezone, input_datetime_format='%Y-%m-%d %H:%M:%S'):
        tzlist = {
            'HT': 'US/Hawaii',
            'AT': 'US/Alaska',
            'PT': 'US/Pacific',
            'MT': 'US/Mountain',
            'CT': 'US/Central',
            'ET': 'US/Eastern'
        }
        input_datetime = datetime.strptime(input_datetime_str, input_datetime_format)
        local = pytz.timezone(tzlist[local_timezone])
        local_datetime = local.localize(input_datetime)
        utc_datetime = local_datetime.astimezone(pytz.utc)

        return utc_datetime

    def expected_timestamp(vendor, st_time: datetime, ed_time: datetime):
        datetime_list = []
        if vendor == 'davis':
            st_time += timedelta(minutes=5)
            while st_time <= ed_time:
                st_time -= timedelta(minutes=st_time.minute % 5,
                                     seconds=st_time.second,
                                     microseconds=st_time.microsecond)
                print(st_time)
                datetime_list.append(st_time)
                st_time += timedelta(minutes=5)
        elif vendor == 'rainwise':
            if st_time.minute % 15 == 0:
                print(st_time)
                datetime_list.append(st_time)
            st_time += timedelta(minutes=15)
            while st_time <= ed_time:
                st_time -= timedelta(minutes=st_time.minute % 15,
                                     seconds=st_time.second,
                                     microseconds=st_time.microsecond)

                print(st_time)
                datetime_list.append(st_time)
                st_time += timedelta(minutes=15)
        elif vendor == 'spectrum':
            if st_time.minute % 5 == 0:
                print(st_time)
                datetime_list.append(st_time)
            st_time += timedelta(minutes=5)
            while st_time < ed_time:
                st_time -= timedelta(minutes=st_time.minute % 5,
                                     seconds=st_time.second,
                                     microseconds=st_time.microsecond)
                print(st_time)
                datetime_list.append(st_time)
                st_time += timedelta(minutes=5)
        elif vendor in ['onset', 'zentra']:
            if st_time.minute % 5 == 0:
                print(st_time)
                datetime_list.append(st_time)
            st_time += timedelta(minutes=5)
            while st_time <= ed_time:
                st_time -= timedelta(minutes=st_time.minute % 5,
                                     seconds=st_time.second,
                                     microseconds=st_time.microsecond)
                print(st_time)
                datetime_list.append(st_time)
                st_time += timedelta(minutes=5)

        return sorted(datetime_list)

    def init_transformed_resp(vendor, st_time, ed_time):
        dt_list = Utilities.expected_timestamp(vendor, st_time, ed_time)
        measurement_list = list()
        for dt_elem in dt_list:
            temp_dic = {
                "station_id": None,
                "request_datetime": None,
                "data_datetime": dt_elem.strftime('%Y-%m-%d %H:%M:%S'),
                "atemp": None,
                "pcpn": None,
                "relh": None
            }
            measurement_list.append(temp_dic)
        # print(measurement_list)
        return measurement_list

    def search_timestamp(transf_resp: list, input_datetime):
        if transf_resp is None:
            return None
        if len(transf_resp) == 0:
            return -1
        for x in range(len(transf_resp)):
            if input_datetime == transf_resp[x]['data_datetime']:
                return x
        return -1

    def insert_resp(transformed_resp: list, trasrec_dict: dict):
        resp_index = Utilities.search_timestamp(transformed_resp, trasrec_dict['data_datetime'])
        if resp_index is None:
            raise Exception("transformed_resp is None")
        elif resp_index == -1:
            transformed_resp.append(trasrec_dict)
        else:
            for k, v in trasrec_dict.items():
                if v is not None:
                    transformed_resp[resp_index][k] = v
        return transformed_resp
