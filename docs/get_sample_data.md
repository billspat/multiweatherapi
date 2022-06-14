## Sample Data Retrieval 

Sample data retrieval tool allows you to easily get raw API response (JSON) and the transformed API response of your choice among the following weather station vendors (i.e., Zentra, Spectrum, Onset/Hobo, Rainwise, Davis, Campbell)

### Requirement

- Python 3.6 or higher
- [Requests](https://docs.python-requests.org/en/latest/)
- [pytz](https://pythonhosted.org/pytz/)
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/)

Required packages may be installed by following command:

```bash
$ pip install -r requirements.txt
```

> NOTE: In order for this program to run correctly, a configuration file named*** `.env`*** is required in the root folder.

### Example Usage

Requires ***TWO*** arguments

- **vendor** (str): Station vendor name of your interest (e.g., Zentra, Spectrum, Davis, Onset, Rainwise, Campbell)
- **out_dir** (str): Absolute path to directory where data output would be generated
  - JSON formatted files woud be generated

> NOTE: If either of them is missing, program shows error messages with usage

```bash
$ python get_sample_data.py 
usage: get_sample_data.py [-h] [--start_datetime START_DATETIME] [--end_datetime END_DATETIME]
                          [--station_timezone STATION_TIMEZONE]
                          vendor out_dir
get_sample_data.py: error: the following arguments are required: vendor, out_dir
```

Optional arguments

|         Name          |                    Description                    |            Default            |
| :-------------------: | :-----------------------------------------------: | :---------------------------: |
|  start_datetime, st   | start date and time in YYYY-MM-DD HH:MM:SS format | 2hrs before current date/time |
|   end_datetime, ed    |  end date and time in YYYY-MM-DD HH:MM:SS format  | 1hr before current date/time  |
| station_timezone, stz |   Time zone information for the weather station   |              ET               |

> NOTE: Unlike Python binding for each station vendor, `start_datetime` and `end_datetime` expect end-user's ***LOCAL TIME***. This design choice is made to help end-users conveniently specify time span and not have to worry about converting to UTC time zone by themselves. That is also the reason why `station_timezone` argument must be specified if end-user decides to provide one's own time span.

> NOTE: If optional arguments are omitted, program assumes the weather station is in US/Eastern time zone and polls weather station data between 2hrs before current time and 1hr before current time (1hr time span)   

```bash
$ python get_sample_data.py -h
usage: get_sample_data.py [-h] [--start_datetime START_DATETIME] [--end_datetime END_DATETIME]
                          [--station_timezone STATION_TIMEZONE]
                          vendor out_dir

positional arguments:
  vendor               Station vendor name (zentra, spectrum, davis, onset, rainwise, campbell)
  out_dir              Path to data directory where output file will be generated

optional arguments:
  -h, --help            show this help message and exit
  --start_datetime START_DATETIME, -st START_DATETIME
                        start date and time in YYYY-MM-DD HH:MM:SS format
  --end_datetime END_DATETIME, -ed END_DATETIME
                        end date and time in YYYY-MM-DD HH:MM:SS format
  --station_timezone STATION_TIMEZONE, -stz STATION_TIMEZONE
                        Time zone information for the weather station (HT, AT, PT, MT, CT, ET)
```

1. Execute with only ***required*** arguments:

```bash
$ python get_sample_data.py rainwise /Users/jhp/Desktop/

2022-06-14 18:10:53.341635+00:00
UTC Start date: 2022-06-14 16:10:53.341682+00:00, local time zone: ET
Local time Start date: 2022-06-14 12:10:53.341682-04:00
UTC End date: 2022-06-14 17:10:53.341682+00:00, local time zone: ET
Local time End date: 2022-06-14 13:10:53.341682-04:00
[{'station_id': '200000000500', 'request_datetime': '2022-06-14 14:10:53', 'data_datetime': '2022-06-14 12:15:00', 'atemp': 22.9, 'pcpn': 0.0, 'relh': '84'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:10:53', 'data_datetime': '2022-06-14 12:30:00', 'atemp': 23.1, 'pcpn': 0.0, 'relh': '84'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:10:53', 'data_datetime': '2022-06-14 12:45:00', 'atemp': 23.1, 'pcpn': 0.0, 'relh': '84'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:10:53', 'data_datetime': '2022-06-14 13:00:00', 'atemp': 23.2, 'pcpn': 0.0, 'relh': '85'}]
```

2. Execute with optional arguments:

```bash
$ python get_sample_data.py -st "2022-06-14 10:00:00" -ed "2022-06-14 11:00:00" -stz "ET" rainwise /Users/jhp/Desktop/

UTC Start date: 2022-06-14 14:00:00+00:00, local time zone: ET
Local time Start date: 2022-06-14 10:00:00-04:00
UTC End date: 2022-06-14 15:00:00+00:00, local time zone: ET
Local time End date: 2022-06-14 11:00:00-04:00
[{'station_id': '200000000500', 'request_datetime': '2022-06-14 14:18:03', 'data_datetime': '2022-06-14 10:00:00', 'atemp': 19.6, 'pcpn': 0.0, 'relh': '94'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:18:03', 'data_datetime': '2022-06-14 10:15:00', 'atemp': 19.8, 'pcpn': 0.0, 'relh': '93'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:18:03', 'data_datetime': '2022-06-14 10:30:34', 'atemp': -17.8, 'pcpn': 0.0, 'relh': {}}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:18:03', 'data_datetime': '2022-06-14 10:45:00', 'atemp': 20.3, 'pcpn': 0.0, 'relh': '90'}, {'station_id': '200000000500', 'request_datetime': '2022-06-14 14:18:03', 'data_datetime': '2022-06-14 11:00:00', 'atemp': 20.9, 'pcpn': 0.0, 'relh': '89'}]
```

