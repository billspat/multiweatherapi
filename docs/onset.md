# Onset Weather Stations

### Authentication

Onset weather station API requires ***client_id*** and ***client_secret*** that are assigned by Onset and use those to generate ***bearer token***.

To create, following request/call needs to be made:

| Component | Contents                                                     |
| --------- | ------------------------------------------------------------ |
| Header    | Accept: application/json, Content-Type: application/x-www-form-urlencoded |
| Method    | POST                                                         |
| URL       | https://webservice.hobolink.com/ws/auth/token                |
| Data      | "grant_type" : "client_credentials", "client_id" : "CLIENT_ID", "client_secret" : "CLIENT_SECRET" |

> NOTE: `client_id` and `client_secret` is **different** from the login credentials for hobolink.com

### Endpoint in Action

1. Get data via File Endpoint

   - In order to collect measurement data from a station over a specified time period, following request/call needs to be made:

   | Component | Contents                                                     |
   | --------- | ------------------------------------------------------------ |
   | Header    | Accept: application/json, Authorization: Bearer ACCESS_TOKEN |
   | Method    | GET                                                          |
   | URL       | https://webservice.hobolink.com/ws/data/file/{format}/user/{userId} |

   - Parameters

   | Name            | Description                                                  | Data Type | Parameter Type | Required |
   | --------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | format          | The format data should be returned in. (Only JSON is supported) | str       | Path           | Y        |
   | userId          | Numeric ID of the user account                               | str       | Path           | Y        |
   | loggers         | Comma-delimited list of logger serial numbers that data should be grabbed for. List is limited to 10 different loggers at a time | str       | Query          | Y        |
   | start_date_time | The date furthest in the past data should be grabbed for. Should be in the format yyyy-MM-dd HH:mm:ss in **UTC time zone** | str       | Query          | Y        |
   | end_date_time   | This is only needed if time frame querying is desired (see later section). Should be in the format yyyy-MM-dd HH:mm:ss in **UTC time zone** | str       | Query          | Y        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=244da747aeba49abb5c9d2504fa5fc56&e=ZQDxlP) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=55ky0M).
   
     > NOTE: userId may be pulled from the HOBOlink URL: www.hobolink.com/users/<userId>
   
4. Addtional Endpoint information

   - Full information about the Onset API can be found at https://webservice.hobolink.com/ws/data/info/index.html. This site includes all available API calls, their correct use and formatting.

### Python Binding

- Required Parameters

| Name          | Contents                                                     | Type     |
| ------------- | ------------------------------------------------------------ | -------- |
| sn            | Logger serial number that data should be grabbed for         | str      |
| client_id     | client-specific value provided by Onset                      | str      |
| client_secret | client-specific value provided by Onset                      | str      |
| ret_form      | The format data should be returned in. (Only JSON is supported) | str      |
| user_id       | Numeric ID of the user account                               | str      |
| start_date    | Start date and time (UTC time zone expected)                 | datetime |
| end_date      | End date and time (UTC time zone expected)                   | datetime |

> NOTE: start_date & end_date must be in UTC time zone for Python binding to correctly interpret date/time

- Usage

```python
params = {
    'sn': SERIAL_NO,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'ret_form': 'JSON',
  	'user_id': USER_ID
    'start_date': datetime.strptime('11-19-2021 14:00', '%m-%d-%Y %H:%M'),
    'end_date': datetime.strptime('11-19-2021 16:00', '%m-%d-%Y %H:%M')
}
oparams = OnsetParam(**params)
oreadings = OnsetReadings(oparams)
print(oreadings.response) # print raw JSON response
print(oreadings.parsed_resp) # print parsed result in list of dict format
```

### Data Matching/Parsing

TBA