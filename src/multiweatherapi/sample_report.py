import argparse
import json
import pytz
from os import getenv
from dotenv import load_dotenv
from os.path import isfile, isdir, join
from datetime import datetime, timezone, timedelta

from src.multiweatherapi import multiweatherapi


def gen_sample_report(vendor: str, out_dir: str, start_datetime=None, end_datetime=None, tz=None):
    load_dotenv()
    vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise', 'campbell']
    if not vendor or vendor == '' or vendor.lower() not in vendor_list:
        raise Exception('"vendor" must be specified and in the approved vendor list.')
    if not out_dir or not isdir(out_dir):
        raise Exception("out_dir must be specified and/or out_dir folder does not exist")
    if start_datetime and not isinstance(start_datetime, datetime):
        raise Exception('start_datetime must be datetime.datetime instance')
    if end_datetime and not isinstance(end_datetime, datetime):
        raise Exception('end_datetime must be datetime.datetime instance')
    if start_datetime and end_datetime and (start_datetime > end_datetime):
        raise Exception('start_datetime must be earlier than end_datetime')
    if not start_datetime or not end_datetime:
        start_datetime = datetime.now(timezone.utc) - timedelta(hours=24)
        end_datetime = start_datetime + timedelta(hours=2)

    params = json.loads(getenv(vendor.upper()))
    params['start_datetime'] = start_datetime
    params['end_datetime'] = end_datetime
    params['tz'] = tz if tz else 'ET'
    resp = multiweatherapi.get_reading(vendor, **params)
    with open(join(out_dir, vendor + '.json'), 'w') as wf:
        json.dump(resp.resp_raw, wf, indent=2)
    print(resp.resp_raw)


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
    # gen_sample_report('rainwise', '/Users/jhp/Desktop/tests/sample2')
    parser = argparse.ArgumentParser()  # command-line arguments parsing module
    parser.add_argument('vendor', help='Station vendor name (zentra, spectrum, davis, onset, rainwise, campbell)')
    parser.add_argument('out_dir', help='Path to data directory where output file will be generated')
    parser.add_argument('start_datetime', help='start date and time in YYYY-MM-DD HH:MM:SS format', default=None)
    parser.add_argument('end_datatime', help='end date and time in YYYY-MM-DD HH:MM:SS format', default=None)
    parser.add_argument('timezone', help='Time zone information for start & end datetime (HT, AT, PT, MT, CT, ET)',
                        default=None)
    args = parser.parse_args()

    vendor = args.vendor
    out_dir = args.out_dir
    start_datetime = args.start_datetime
    end_datetime = args.end_datetime
    timezone = args.timezone

    if start_datetime and end_datetime and timezone:
        start_datetime = format_datetime(start_datetime, timezone)
        end_datetime = format_datetime(end_datetime, timezone)
        gen_sample_report(vendor, out_dir, start_datetime, end_datetime, timezone)
    else:
        gen_sample_report(vendor, out_dir)
