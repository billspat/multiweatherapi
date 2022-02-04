# Davis Weather Stations

### Authentication

Davis (WeatherLink) weather station API requires an ***API Key***, an ***API Secret***, a request ***timestamp*** and a calculated ***API Signature*** for authenticating API requests.

- **API Key**

  API Key is a unique ID that identifies the API user making the API call. API Key must be passed as a query parameter in all API request.

  

- **API Secret**

  API Secret is a secret value that is used to calculate a signature for each API request.

  > NOTE: API Secret must be protected and if compromised it wll allow other s to access API while pretending to be the user

  

- **API Request Timestamp**

  API request timestamp is the Unix timestamp at the time the API request is being generated. Every request to the WeatherLink v2 API must use the current Unix timestamp and the API signature must be recomputed to account for the new timestamp on each request.

  > NOTE: The purpose of the timestamp is to prevent request replay attacks.

  

- **API Signature**

  The API Signature process takes all of the request parameters and the API Secret and computes a fingerprint-like value that represents the request. Every request to the WeatherLink v2 API must calculate a new signature for the parameters being sent in the API call. 

  > NOTE: This API Signature is used to prevent API request parameter tampering.

  To calculate the signature use the HMAC SHA-256 algorithm with the concatenated parameter string as the message and the API Secret as the HMAC secret key. The resulting computed HMAC value as a hexadecimal string is the API Signature. Sample of computing API Signature is shown below:

  ```python
  def compute_signature(self):
    params = {
      'api-key': self.apikey,
      'station-id': self.sn,
      't': self.t
    }
    if self.start_date and self.end_date:
      params['start-timestamp'] = self.start_date
      params['end-timestamp'] = self.end_date
  
    params = collections.OrderedDict(sorted(params.items()))
    for key in params:
      print("Parameter name: \"{}\" has value \"{}\"".format(key, params[key]))
  
    data = ""
    for key in params:
      data = data + key + str(params[key])
    print("Data string to hash is: \"{}\"".format(data))
  
    self.apisig = hmac.new(
      self.apisec.encode('utf-8'),
      data.encode('utf-8'),
      hashlib.sha256
    ).hexdigest()
    print("API Signature is: \"{}\"".format(self.apisig))
  ```

### Endpoint in Action

1. Get current data

   - In order to collect current measurement data from a station, following request/call needs to be made:

   | Component | Contents                                             |
   | --------- | ---------------------------------------------------- |
   | Header    | Accept: application/json                             |
   | Method    | GET                                                  |
   | URL       | https://api.weatherlink.com/v2/current/{station-id}/ |

   - Parameters

   | Name          | Description                                | Data Type | Parameter Type | Required |
   | ------------- | ------------------------------------------ | --------- | -------------- | -------- |
   | station-id    | A single station ID                        | str       | Path           | Y        |
   | api-key       | API Key                                    | str       | Query          | Y        |
   | api-signature | API Signature                              | str       | Query          | Y        |
   | t             | Unix timestamp when the query is submitted | int       | Query          | Y        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=a80bb057384c4a6ba95f89c7f46fc160&e=cJT5Em) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=55ky0M).
   
1. Get historic data 

   - In order to collect measurement data from a station over a specified time period, following request/call needs to be made:

   | Component | Contents                                              |
   | --------- | ----------------------------------------------------- |
   | Header    | Accept: application/json                              |
   | Method    | GET                                                   |
   | URL       | https://api.weatherlink.com/v2/historic/{station-id}/ |

   - Parameters

   | Name            | Description                                                  | Data Type | Parameter Type | Required |
   | --------------- | ------------------------------------------------------------ | --------- | -------------- | -------- |
   | station-id      | A single station ID                                          | str       | Path           | Y        |
   | api-key         | API Key                                                      | str       | Query          | Y        |
   | api-signature   | API Signature                                                | str       | Query          | Y        |
   | t               | Unix timestamp when the query is submitted                   | int       | Query          | Y        |
   | start-timestamp | Unix timestamp marking the beginning of the data requested. Must be earlier than end-timestamp but not more than 24 hours earlier. | int       | Query          | Y        |
   | end-timestamp   | Unix timestamp marking the end of the data requested. Must be later than start-timestamp but not more than 24 hours later. | int       | Query          | Y        |
   
   - Sample output [JSON File](https://michiganstate.sharepoint.com/sites/Geography-EnviroweatherTeam/_layouts/15/download.aspx?UniqueId=91c9b9303d9f453897e04104f7cca03f&e=yNpYKQ) may be viewed from the project [SharePoint Folder](https://michiganstate.sharepoint.com/:f:/r/sites/Geography-EnviroweatherTeam/Shared%20Documents/Data%20on%20Demand/ADS%20ENVWX%20API%20Project/Vendor%20API%20and%20station%20info/Sample%20Weather%20Data%20Output?csf=1&web=1&e=55ky0M).
   
3. Addtional Endpoint information

   - Full information about the Davis (WeatherLink) API can be found at https://weatherlink.github.io/v2-api/api-reference. This site includes all available API calls, their correct use and formatting.

### Python Binding

- Required Parameters

| Name       | Contents                           | Type     |
| ---------- | ---------------------------------- | -------- |
| sn         | Station ID                         | str      |
| apikey     | Client-specific value              | str      |
| apisec     | Client-specific value              | str      |
| start_date | Start date and time (UTC expected) | datetime |
| end_date   | End date and time (UTC expected)   | datetime |

> NOTE: For date/time range to correctly work, both parameters should be in UTC timezone

- Usage

```python
params = {
    'sn': STATION_ID,
    'apikey': API_KEY,
    'apisec': API_SECURITY,
    'start_date': datetime.strptime('11-19-2021 14:00', '%m-%d-%Y %H:%M'),
    'end_date': datetime.strptime('11-19-2021 16:00', '%m-%d-%Y %H:%M')
}
dparams = DavisParam(**params)
dreadings = DavisReadings(dparams)
print(dreadings.response) # print raw JSON response
print(dreadings.parsed_resp) # print parsed result in list of dict format
```

### Data Matching/Parsing

TBA