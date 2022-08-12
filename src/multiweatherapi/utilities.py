from datetime import datetime
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