from datetime import datetime
import pprint
import pytz
class Utilities:
    def case_insensitive_key(this_dict, this_key):
        this_key = this_key.lower()
        value = [this_dict[key] for key in this_dict if key.lower() == this_key][0]
        return value.replace('"', '')
        
    def convert_to_dict(resp_raw, davisParm = None):
    # Takes a resp_raw list object and converts it to a straight dictionary.
        new_raw = {}
        new_raw = resp_raw[0]

        if davisParm:
            end = len(davisParm.date_tuple_list) - 1
            new_raw['start_datetime'] = datetime.fromtimestamp(davisParm.date_tuple_list[0][0], pytz.timezone('America/Detroit')).strftime('%Y-%m-%d')
            new_raw['end_datetime'] = datetime.fromtimestamp(davisParm.date_tuple_list[end][1], pytz.timezone('America/Detroit')).strftime('%Y-%m-%d')

        # Loop through the resp_raw items, starting with index 1.  If this is a Davis station, there could be multiple items.  
        # Append each item to a temporary dictionary.
        temp = list()
        for i in range(1, len(resp_raw)):
            temp.append(resp_raw[i])
        
        # Set the api_output dictionary element to the temporary list.
        new_raw['api_output'] = temp

        return new_raw