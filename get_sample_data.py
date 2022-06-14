import argparse
import json
import pytz
from os import getenv
from dotenv import load_dotenv
from os.path import isdir, join
from datetime import datetime, timezone, timedelta

from src.multiweatherapi import multiweatherapi


def get_sample_data(vendor_name: str, outdir: str, st_datetime=None, ed_datetime=None, station_tz=None):
    load_dotenv()
    vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise', 'campbell']
    if not vendor_name or vendor_name == '' or vendor_name.lower() not in vendor_list:
        raise Exception('"vendor_name" must be specified and in the approved vendor list.')
    if not outdir or not isdir(outdir):
        raise Exception("outdir must be specified and/or out_dir folder does not exist")
    if st_datetime and not isinstance(st_datetime, datetime):
        raise Exception('st_datetime must be datetime.datetime instance')
    if ed_datetime and not isinstance(ed_datetime, datetime):
        raise Exception('ed_datetime must be datetime.datetime instance')
    if st_datetime and ed_datetime and (st_datetime > ed_datetime):
        raise Exception('st_datetime must be earlier than ed_datetime')
    if not st_datetime or not ed_datetime:
        print(datetime.now(timezone.utc))
        st_datetime = datetime.now(timezone.utc) - timedelta(hours=2)
        ed_datetime = st_datetime + timedelta(hours=1)

    params = json.loads(getenv(vendor_name.upper()))
    params['start_datetime'] = st_datetime
    params['end_datetime'] = ed_datetime
    params['tz'] = station_tz if station_tz else 'ET'
    resp = multiweatherapi.get_reading(vendor_name, **params)
    with open(join(outdir, vendor_name + '_raw.json'), 'w') as wf:
        json.dump(resp.resp_raw, wf, indent=2)
    with open(join(outdir, vendor_name + '_transform.json'), 'w') as wf:
        json.dump(resp.resp_transformed, wf, indent=2)
    # print("Raw Response:\n", resp.resp_raw)
    # print("\nTransformed:\n", resp.resp_transformed)


def format_datetime(input_datetime_str, local_timezone):
    tzlist = {
        'HT': 'US/Hawaii',
        'AT': 'US/Alaska',
        'PT': 'US/Pacific',
        'MT': 'US/Mountain',
        'CT': 'US/Central',
        'ET': 'US/Eastern'
    }
    input_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M:%S')
    local = pytz.timezone(tzlist[local_timezone])
    local_datetime = local.localize(input_datetime)
    utc_datetime = local_datetime.astimezone(pytz.utc)

    return utc_datetime


if __name__ == '__main__':
    parser = argparse.ArgumentParser()  # command-line arguments parsing module
    parser.add_argument('vendor', help='Station vendor name (zentra, spectrum, davis, onset, rainwise, campbell)')
    parser.add_argument('out_dir', help='Path to data directory where output file will be generated')
    parser.add_argument('--start_datetime', '-st',
                        help='start date and time in YYYY-MM-DD HH:MM:SS format', default=None)
    parser.add_argument('--end_datetime', '-ed', help='end date and time in YYYY-MM-DD HH:MM:SS format', default=None)
    parser.add_argument('--station_timezone', '-stz',
                        help='Time zone information for the weather station (HT, AT, PT, MT, CT, ET)', default=None)
    args = parser.parse_args()

    vendor = args.vendor
    out_dir = args.out_dir
    start_datetime = args.start_datetime
    end_datetime = args.end_datetime
    station_timezone = args.station_timezone

    if start_datetime and end_datetime and station_timezone:
        start_datetime = format_datetime(start_datetime, station_timezone)
        end_datetime = format_datetime(end_datetime, station_timezone)
        get_sample_data(vendor, out_dir, start_datetime, end_datetime, station_timezone)
    else:
        get_sample_data(vendor, out_dir)
