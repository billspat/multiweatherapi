import pprint
class Utilities:
    def convert_to_dict(resp_raw):
    # Takes a resp_raw list object and converts it to a straight dictionary.
        new_raw = {}
        new_raw = resp_raw[0]
        new_raw['api_output'] = resp_raw[1]

        return new_raw