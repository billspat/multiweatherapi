import json

from .davis import DavisParam, DavisReadings
from .spectrum import SpectrumParam, SpectrumReadings
from .zentra import ZentraParam, ZentraReadings
from .onset import OnsetParam, OnsetReadings
from .rainwise import RainwiseParam, RainwiseReadings
from .campbell import CampbellParam, CampbellReadings
from .utilities import Utilities

__version__ = '0.0.25'


class ApiWrapper:
    """
    This class is a wrapper for all the various vendor API classes that make up MWAPI.
    """
    def __init__(self, params: dict):
        """
        This module initializes an ApiWrapper object.

        Parameters
        ----------
        params : dict
                 The parameters that will be sent to the vendor API.
        """
        
        self.vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise', 'campbell']
        self.vendor = params.get('vendor', None)
        self.params = params
        self.resp_raw = None
        self.resp_transformed = None
        self.resp_debug = None

        self.check_params()

    def check_params(self):
        """
        This module checks to see if the vendor is specified in the parmeter dictionary and is in the list of approved vendors.

        Raises
        ------
        Exception
           If the vendor is non-existent or is not in the list of approved vendors.
        """

        if self.vendor is None or self.vendor.lower() not in self.vendor_list:
            raise Exception('"vendor" must be specified and in the approved vendor list.')
        else:
            self.vendor = self.vendor.lower()

    def get_reading(self):
        """
        This module will do the following:
        1) Create the parameter object that matches the vendor.
        2) Checks to make sure that no entry in the parameter dictionary is the empty string.
        3) Checks to make sure that all required parameters are present and are of the correct type and properly
           formats any dates.
        4) Create the readings object for the vendor.
        5) Gets the readings from the vendor API.
        6) Gets the resp_raw object (which holds the data as it was received from the API) and converts it into a dictionary.
        7) Gets the resp_transformed object (which hold the data after it has been transformed into a DB compatible format).

        If there is an exception raised by the vendor parameter or readings classes, then this method will create an error message
        which will be placed in the raw_data table to serve as an easily accessible log.
        """
        if self.vendor == 'zentra':
            try:
                zparam = ZentraParam(sn=self.params.get('sn', None),
                                    token=self.params.get('token', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    start_mrid=self.params.get('start_mrid', None),
                                    end_mrid=self.params.get('end_mrid', None),
                                    tz=self.params.get('tz', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                zparam._process()
                zreadings = ZentraReadings(zparam)
                zreadings._process(zparam)
                self.resp_raw = zreadings.response
                self.resp_transformed = zreadings.transformed_resp
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed)
                self.resp_debug = zreadings.debug_info
            except Exception as error:
                zreadings = ZentraReadings(zparam)
                self.resp_raw = Utilities.create_error_response('ZENTRA', zparam, zreadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)                     
            return self                
            return self
        elif self.vendor == 'davis':
            try:
                dparam = DavisParam(sn=self.params.get('sn', None),
                                    apikey=self.params.get('apikey', None),
                                    apisec=self.params.get('apisec', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    tz=self.params.get('tz', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                dparam._process()
                dreadings = DavisReadings(dparam)
                dreadings._process(dparam)
                self.resp_raw = dreadings.response
                self.resp_transformed = dreadings.transformed_resp
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed, dparam)
                self.resp_debug = dreadings.debug_info
            except Exception as error:
                dreadings = DavisReadings(dparam)
                self.resp_raw = Utilities.create_error_response('DAVIS', dparam, dreadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)                     
            return self
        elif self.vendor == 'spectrum':
            try:
                sparam = SpectrumParam(sn=self.params.get('sn', None),
                                    apikey=self.params.get('apikey', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    date=self.params.get('date', None),
                                    tz=self.params.get('tz', None),
                                    count=self.params.get('count', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                sparam._process()
                sreadings = SpectrumReadings(sparam)
                sreadings._process(sparam)
                self.resp_raw = sreadings.response
                self.resp_transformed = sreadings.transformed_resp
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed)
                self.resp_debug = sreadings.debug_info
            except Exception as error:
                sreadings = SpectrumReadings(sparam)
                self.resp_raw = Utilities.create_error_response('SPECTRUM', sparam, sreadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)     
            return self
        elif self.vendor == 'onset':
            try:
                oparam = OnsetParam(sn=self.params.get('sn', None),
                                    client_id=self.params.get('client_id', None),
                                    client_secret=self.params.get('client_secret', None),
                                    ret_form=self.params.get('ret_form', None),
                                    user_id=self.params.get('user_id', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    tz=self.params.get('tz', None),
                                    sensor_sn=self.params.get('sensor_sn', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                oparam._process()                                
                oreadings = OnsetReadings(oparam)
                oreadings._process(oparam)
                self.resp_raw = oreadings.response
                self.resp_transformed = oreadings.transformed_resp
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed)
                self.resp_debug = oreadings.debug_info
            except Exception as error:
                oreadings = OnsetReadings(oparam)
                self.resp_raw = Utilities.create_error_response('ONSET', oparam, oreadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)                           
            return self
        elif self.vendor == 'rainwise':
            try:
                rparam = RainwiseParam(username=self.params.get('username', None),
                                    sid=self.params.get('sid', None),
                                    pid=self.params.get('pid', None),
                                    mac=self.params.get('mac', None),
                                    ret_form=self.params.get('ret_form', None),
                                    interval=self.params.get('interval', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    tz=self.params.get('tz', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                rparam._process()    
                rreadings = RainwiseReadings(rparam)
                rreadings._process(rparam)
                self.resp_raw = rreadings.response
                self.resp_transformed = rreadings.transformed_resp              
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed)
                self.resp_debug = rreadings.debug_info
            except Exception as error:
                rreadings = RainwiseReadings(rparam)
                self.resp_raw = Utilities.create_error_response('RAINWISE', rparam, rreadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
            return self
        elif self.vendor == 'campbell':
            try:
                cparam = CampbellParam(username=self.params.get('username', None),
                                    user_passwd=self.params.get('user_passwd', None),
                                    station_id=self.params.get('station_id', None),
                                    station_lid=self.params.get('station_lid', None),
                                    start_datetime=self.params.get('start_datetime', None),
                                    end_datetime=self.params.get('end_datetime', None),
                                    tz=self.params.get('tz', None),
                                    binding_ver=__version__)
                Utilities.check_empty_str(self.params)
                cparam._process()                                    
                creadings = CampbellReadings(cparam)
                creadings._process(cparam)
                self.resp_raw = creadings.response
                self.resp_transformed = creadings.transformed_resp
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, self.resp_transformed) 
                self.resp_debug = creadings.debug_info
            except Exception as error:
                creadings = CampbellReadings(cparam)
                self.resp_raw = Utilities.create_error_response('CAMPBELL', cparam, creadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)           
            return self


def get_reading(vendor: str, **params) -> json:
    """
    This method will call the vendor API and retrieve the data.

    Returns
    -------
    The readings from the vendor API.
    """
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()


def get_version() -> str:
    """
    This module returns the version number of the mwapi package.

    Returns
    -------
    The package version.
    """
    return __version__
