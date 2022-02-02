# Spectrum Weather Stations

### Authentication

Spectrum weather station API requires an ***API Key*** that is a customer-specific token, for authenticating API requests.

> NOTE: It should be of the form `customerApiKey=<API_KEY>` as a query parameter.

### Endpoint in Action

1. Get the 50 most recent sensor data records for a specific customer device

   - In order to get readings for a given device, following request/call needs to be made:

   | Component | Contents                                              |
   | --------- | ----------------------------------------------------- |
   | Header    | Accept: application/json                              |
   | Method    | GET                                                   |
   | URL       | https://api.specconnect.net:6703/api/Customer/GetData |

   - Parameters

   | Name           | Description                                                  | Data Type | Parameter Type | Required |
   | -------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | customerApiKey | Customer API Key                                             | str       | Query          | Y        |
   | serialNumber   | Device Serial Number                                         | str       | Query          | Y        |
   | optValues      | Additional (comma-separated) calculated values (vpd, dewPoint, wetBulb, deltaT, heatIndex, absoluteHumidity) | str       | Query          | N        |
   | optUnits       | Comma-separated list of unit preferences for temperature, rainfall, pressure, (wind-)speed and compaction sensors | str       | Query          | N        |
   
1. Get sensor data for a specific customer device for a specific date/time range

   - In order to get readings for a given device over a specified time period, following request/call needs to be made:

   | Component | Contents                                                     |
   | --------- | ------------------------------------------------------------ |
   | Header    | Accept: application/json                                     |
   | Method    | GET                                                          |
   | URL       | https://api.specconnect.net:6703/api/Customer/GetDataInDateTimeRange |

   - Parameters

   | Name           | Description                                                  | Data Type | Parameter Type | Required |
   | -------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | customerApiKey | Customer API Key                                             | str       | Query          | Y        |
   | serialNumber   | Device Serial Number                                         | str       | Query          | Y        |
   | startDate      | Start of Date Range (e.g., 2021-08-01 00:00)                 | datetime  | Query          | Y        |
   | endDate        | End of Date Range (e.g., 2021-08-31 23:59)                   | datetime  | Query          | Y        |
   | optValues      | Additional (comma-separated) calculated values (vpd, dewPoint, wetBulb, deltaT, heatIndex, absoluteHumidity) | str       | Query          | N        |
   | optUnits       | Comma-separated list of unit preferences for temperature, rainfall, pressure, (wind-)speed and compaction sensors | str       | Query          | N        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=948b7aa84f084afe8e6b25f0e15844c8&e=A2fnue) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=55ky0M).
   
3. Get sensor data for a specific customer device for a specific date

   - In order to get readings for a given device over a specified date, following request/call needs to be made:

   | Component | Contents                                                    |
   | --------- | ----------------------------------------------------------- |
   | Header    | Accept: application/json                                    |
   | Method    | GET                                                         |
   | URL       | https://api.specconnect.net:6703/api/Customer/GetDataByDate |

      - Parameters

   | Name           | Description                                                  | Data Type | Parameter Type | Required |
   | -------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | customerApiKey | Customer API Key                                             | str       | Query          | Y        |
   | serialNumber   | Device Serial Number                                         | str       | Query          | Y        |
   | date           | Date (e.g., 2021-08-01)                                      | datetime  | Query          | Y        |
   | optValues      | Additional (comma-separated) calculated values (vpd, dewPoint, wetBulb, deltaT, heatIndex, absoluteHumidity) | str       | Query          | N        |
   | optUnits       | Comma-separated list of unit preferences for temperature, rainfall, pressure, (wind-)speed and compaction sensors | str       | Query          | N        |

4. Get a specific number of recent sensor data records for a specific customer device

   - In order to get a specific number of readings for a given device, following request/call needs to be made:

   | Component | Contents                                                     |
   | --------- | ------------------------------------------------------------ |
   | Header    | Accept: application/json                                     |
   | Method    | GET                                                          |
   | URL       | https://api.specconnect.net:6703/api/Customer/GetDataByRange |

   - Parameters

   | Name           | Description                                                  | Data Type | Parameter Type | Required |
   | -------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | customerApiKey | Customer API Key                                             | str       | Query          | Y        |
   | serialNumber   | Device Serial Number                                         | str       | Query          | Y        |
   | count          | The number of recent records to retrieve                     | int       | Query          | Y        |
   | optValues      | Additional (comma-separated) calculated values (vpd, dewPoint, wetBulb, deltaT, heatIndex, absoluteHumidity) | str       | Query          | N        |
   | optUnits       | Comma-separated list of unit preferences for temperature, rainfall, pressure, (wind-)speed and compaction sensors | str       | Query          | N        |

5. Addtional Endpoint information

   - Full information about the SpecConnect Customer API can be found at https://api.specconnect.net:6703/Help/. This site includes all available API calls, their correct use and formatting.

### Python Binding

- Required Parameters

| Name       | Contents                            | Type     |
| ---------- | ----------------------------------- | -------- |
| sn         | Device Serial Number (serialNumber) | str      |
| apikey     | API Key (customerApiKey)            | str      |
| start_date | Start date and time                 | datetime |
| end_date   | End date and time                   | datetime |

- Usage

```python
params = {
    'sn': DEVICE_SN,
    'apikey': API_KEY,
    'start_date': datetime.strptime('11-19-2021 14:00', '%m-%d-%Y %H:%M'),
    'end_date': datetime.strptime('11-19-2021 16:00', '%m-%d-%Y %H:%M')
}
sparams = SpectrumParam(**params)
sreadings = SpectrumReadings(sparams)
print(sreadings.response) # print raw JSON response
print(sreadings.parsed_resp) # print parsed result in list of dict format
```

### Data Matching/Parsing

TBA