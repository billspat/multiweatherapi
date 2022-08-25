from datetime import datetime, timedelta
import pytz


class Utilities:
    def case_insensitive_key(this_dict, this_key):
        this_key = this_key.lower()
        value = [this_dict[key] for key in this_dict if key.lower() == this_key][0]
        return value.replace('"', '')
        
    def create_error_response(vendor, parms, readings, error_msg):
    # Create a resp_raw item when there are errors to report.
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
    # Takes a resp_raw list object and converts it to a straight dictionary.
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
        from dateutil.parser import parse

        if isinstance(date, str):
            date = parse(date)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
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
