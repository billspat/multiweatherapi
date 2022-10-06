# Multiweather API (MWAPI) Error Reporting
<hr>

## Business Case

Currently, when MWAPI encounters an error, an exception is raised and MWAPI returns control to the calling program.  The trouble with this approach is that the error either doesn't get into the Azure logs, or is lost within the sheer amount of logging information.  Therefore, it was decided that the raw_data table in the Enviroweather database could be utilized as a way to easily see when if a call to MWAPI failed or succeeded.

## Types of errors
There are two types of errors that can occur within MWAPI: parameter errors and API errors.  We will outline how each should will now be handled:

### Parameter Errors
Parameter errors occur when MWAPI encounters missing or incorrect parameter information.  This could be a missing username for a vendor that requires it, a mistyped station ID, etc.  These errors should be captured by the module that is calling MWAPI and placed into the resp_raw table.

### API Errors
API errors occur when the API being called has encountered an error.  These errors can be due to timeouts, connection failures, authorization failures, etc.  Authorization errors will be handled in the same way as parameter errors, with MWAPI raising an exception and returning control to the caller.  Other API errors will be handled by MWAPI and will be placed in the raw data section of the response object that is returned to the caller.

## MWAPI Error Handling Process
When MWAPI encounters an API error that needs to be reported out to the caller for placement in the raw_data table, the following process will be followed:
1. A "status_code" dictionary entry will be placed in the response object that contains the status code returned by the API.
2. A "error_msg" dictionary entry will be placed in the response object that contains the error message returned by the API.
3. A status field will be added to the raw_data table, which will contain one of these values:
   GOOD if data was returned from the vendor.
   ERROR if no data was returned from the vendor API call.  This could be due to: 
   * Missing or bad parameters
   * API failure
   * The vendor API returned a 200, but there was no data
4. Any transformation of data will be bypassed as there most likely will be no data to process.
5. The response object will be returned to the calling module, which will place that information in the raw_data table.
6. The raw data will be placed in the raw_data table.  This entry will contain the status code and any error messages.
7. A secondary process will be run, either manually or on a to-be-determined schedule that will look for entries with "ERROR" in the status field and call the vendor API to see if that missing data can be retrieved.

## Information that will be stored in the raw_data table:
The following data will be always placed in the raw_data table:

| Data Item              | Description                               |
|------------------------|-------------------------------------------|
| vendor                 | The vendor whose API is being called.     |
| station_id             | The ID of the station being polled.       |
| timezone               | The timezone where the station resides.   |
| start_datetime         | The start of the date range being pulled. |
| end_datetime           | The end of the date range being pulled.   |
| request_time           | The time that the API call was made.      |
| python_binding_version | The version of MWAPI being run.           |

If the call was successful, the raw data returned by the API will also be stored.