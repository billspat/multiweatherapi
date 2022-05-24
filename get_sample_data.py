
from datetime import datetime, timezone, timedelta
import json
import sys
from dotenv import load_dotenv
from src.multiweatherapi import multiweatherapi
import os


load_dotenv()

def get_mw_obj(vendor = 'RAINWISE' ):
    """simple fn to set params to request sample data  """
 
    start_datetime = datetime.now(timezone.utc) - timedelta(hours=2)
    end_datetime  = start_datetime + timedelta(hours=1)
    # read from env var, vendor must be upper case for this

    multiweatherapi_params = json.loads(os.environ[vendor.upper()])
    multiweatherapi_params['start_datetime'] = start_datetime
    multiweatherapi_params['end_datetime'] = end_datetime
    if 'tz' not in multiweatherapi_params.keys(): multiweatherapi_params['tz'] = 'ET' 
    # get data, vendor must be lower for it to work currently 
    mwobj = multiweatherapi.get_reading(vendor.lower(), **multiweatherapi_params)
    return( mwobj)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        vendor = sys.argv[1]
        mwobj = get_mw_obj(vendor)
    else:
        mwobj = get_mw_obj()
    
    mwobj.resp_raw
