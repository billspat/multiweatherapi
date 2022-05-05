# Multiweather API Testing

The multiweather tests can be run using this syntax:
`pytest` - Run the entire test suite
`pytest -k "<keyword>"` - Run all tests whose name contains the keyword. 
&emsp;&emsp;&emsp;Example: `pytest -k "spectrum_good_identifier"`

The test suite expects a .env file to reside in the test directory.  This has entries for each weather station that is to be tested.  There are currently six entries to be defined:
```
zentra_good
davis_good
spectrum_good
onset_good
rainwise_good
campbell_good
```
Sample:

```
zentra_good = {"sn":"[serial]","manufacturer":"[manudacturer]","token":"[token]","apikey":"[apikey]","apisec":"[apisec]","vendor":"[vendor]","description":"[description]","update_freq":"[update frequency in minutes]","client_id":"[client id]","client_secret":"client secret code]","ret_form":"[return format]","user_id":"[user id]","username":"[user name]","password":"[password]"}
```
**Note:** Not all manufacturers use every field.