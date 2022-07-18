import pprint
class Utilities:
    def get_metadata(resp_raw):
    # Takes a resp_raw object and adds metadata.
        new_raw = resp_raw
        # print('*************************************')
        # print('resp_raw is of type ' + str(type(resp_raw)))
        # print('resp_raw = ')
        # print(resp_raw)
        # print('*************************************')
        new_raw[0]['error_msg'] = ''  #TO DO: Get this error message.  Will figure out in another issue.

        return new_raw