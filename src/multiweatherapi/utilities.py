from datetime import datetime
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
        resp_raw = value.replace('"', '')
        return resp_raw
        
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
        Makes sure that the date is a string in the YYYY-MM-DD HH:MM:SS format.

        Parameters
        ----------
        date : datetime or str
               The date we wish to format.

        Returns
        -------
        date : str
               The date as a string and formatted as YYYY-MM-DD HH:MM:SS.

        """
        from dateutil.parser import parse

        if isinstance(date, str):
            date = parse(date)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d %H:%M:%S')

        return date