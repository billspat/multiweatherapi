# Rainwise Weather Stations

### Authentication

Rainwise weather station API does not require real-time authentication process; however end-user/station owners must go through registration process with the Rainwise. By doing so, Rainwise will assign end-user/station owners unique `sid`/`pid` that is required for making API call

> NOTE: Rainwise does provide **public API** that does **not** require registration. The public API has limitation and is intended for accessing current conditions and short period of historical data

### Endpoint in Action

1. Historical Data (get-historical.php)

   - To receive data from a station over a specified time period, following request/call needs to be made:

   | Component | Contents                                                     |
   | --------- | ------------------------------------------------------------ |
   | Method    | GET                                                          |
   | URL       | http://api.rainwise.net/main/v1.5/registered/get-historical.php |
   
   - Parameters
   
   | Name     | Description                                                  | Data Type | Parameter Type | Required |
   | -------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | username | Registered Group Name                                        | str       | Query          | Y        |
   | sid      | Site id, assigned by Rainwise                                | str       | Query          | Y        |
   | pid      | Password id, assigned by Rainwise                            | str       | Query          | Y        |
   | mac      | MAC of the weather station                                   | str       | Query          | Y        |
   | format   | Returns data as XML or JSON, If omitted data is returned as XML | str       | Query          | N        |
   | interval | Data aggregation interval, 1,5,10,15,30 or 60min (default 1min) | int       | Query          | N        |
   | sdate    | Start date and time of the range for the data                | datetime  | Query          | N        |
   | edate    | End date and time of the range for the data                  | datetime  | Query          | N        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=b15e7ca07c2b48aca994aaaaebfe7ba0&e=LOoBjP) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=w3tnnc).
   - Start and End date/time is expected to be in ***Local Time zone***
   
   > NOTE: If `sdate` and `edate` are **not** set, it returns the **last 24 hours**’ worth of data from the current date and time, otherwise the data between the specified ranges is returned. The date range for data is **limited to 7 days** for an interval of **1 minute**. This limit scales with the interval so with an interval of **15 minutes**, the limit will be **105 days**.
   
   
   
4. Addtional Endpoint information

   - Full information about the Campbell Cloud API can be found at https://docs.campbellcloud.io/api/. This site includes all available API calls, their correct use and formatting.
   
   

### Python Binding

- Parameters

| Name       | Description                                                  | Type     | Required |
| ---------- | ------------------------------------------------------------ | -------- | -------- |
| username   | Registered Group Name                                        | str      | Y        |
| sid        | Site id                                                      | str      | Y        |
| pid        | Password id                                                  | str      | Y        |
| mac        | MAC of the weather station                                   | str      | Y        |
| ret_form   | Returns data as XML or JSON, If omitted data is returned as XML | str      | N        |
| interval   | Data aggregation interval, 1,5,10,15,30 or 60min (default 1min) | int      | N        |
| start_date | Start date and time. If omitted set to current time (UTC expected) | datetime | N        |
| end_date   | End date and time. If omitted set to current time (UTC expected) | datetime | N        |

- Usage

```python
params = {
    'username': USERNAME,
    'sid': SID,
    'pid': PID,
    'mac': STATION_MAC_ADDR,
  	'ret_form': 'json',
  	'interval': 1,
    'start_date': datetime.strptime('11-19-2021 14:00', '%m-%d-%Y %H:%M'),
    'end_date': datetime.strptime('11-19-2021 16:00', '%m-%d-%Y %H:%M')
}
rparams = RainwiseParam(**params)
rreadings = RainwiseReadings(rparams)
print(rreadings.response) # print raw JSON response
print(rreadings.parsed_resp) # print parsed result in list of dict format
```

### Data Matching/Parsing

TBA