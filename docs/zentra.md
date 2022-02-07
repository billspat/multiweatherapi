# Zentra Weather Stations

### Authentication

Zentra weather station API requires an ***API Key*** that is an user token each ZENTRA Cloud user has upon creating an account, for authenticating API requests.

> NOTE: It should be of the form `Token <API_TOKEN>` in the request header.

### Endpoint in Action

1. Get reading

   - In order to get readings for a given device, following request/call needs to be made:

   | Component | Contents                                                   |
   | --------- | ---------------------------------------------------------- |
   | Header    | Accept: application/json, Authorization: Token <API_TOKEN> |
   | Method    | GET                                                        |
   | URL       | https://zentracloud.com/api/v3/get_readings/               |

   - Parameters

   | Name          | Description                                                  | Data Type | Parameter Type | Required |
   | ------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | device_sn     | Serial number of device having data requested                | str       | Query          | Y        |
   | start_date    | Start date of time range (Default: first reading of the device, Overrides start_mrid) | str       | Query          | N        |
   | end_date      | End date of time range (Default: last reading of the device, Overrides end_mrid) | str       | Query          | N        |
   | start_mrid    | Start mrid of mrid range (Default: first mrid reading of the device) | int       | Query          | N        |
   | end_mrid      | End mrid of mrid range (Default: end mrid reading of the device) | int       | Query          | N        |
   | output_format | Data structure of the response content (Default: JSON / Options: json, df, csv) | str       | Query          | N        |
   | page_num      | Page number (Default: 1)                                     | int       | Query          | N        |
   | per_page      | Number of readings per page (Default: 500, Max: 2000)        | int       | Query          | N        |
   | sort_by       | Sort the readings in ascending or descending order (Default: descending) | str       | Query          | N        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=13e6919120804d5b9321aba518ce3411&e=RrslcD) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=55ky0M).
   
3. Addtional Endpoint information

   - Full information about the ZENTRA Cloud API can be found at https://zentracloud.com/api/v3/documentation/. This site includes all available API calls, their correct use and formatting.

### Python Binding

- Required Parameters

| Name       | Contents                                     | Type     |
| ---------- | -------------------------------------------- | -------- |
| sn         | Serial number of device (device_sn)          | str      |
| token      | API Key (Client-specific value)              | str      |
| start_date | Start date and time (UTC time zone expected) | datetime |
| end_date   | End date and time (UTC time zone expected)   | datetime |
| start_mrid | Start mrid of mrid range                     | int      |
| end_mrid   | End mrid of mrid range                       | int      |

> NOTE: start_date & end_date must be in UTC time zone for Python binding to correctly interpret date/time

- Usage

```python
params = {
    'sn': DEVICE_SN,
    'token': API_KEY,
    'start_date': datetime.strptime('11-19-2021 14:00', '%m-%d-%Y %H:%M'),
    'end_date': datetime.strptime('11-19-2021 16:00', '%m-%d-%Y %H:%M')
}
zparams = ZentraParam(**params)
zreadings = ZentraReadings(zparams)
print(zreadings.response) # print raw JSON response
print(zreadings.parsed_resp) # print parsed result in list of dict format
```

### Data Matching/Parsing

TBA