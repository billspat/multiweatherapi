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
    def __init__(self, params: dict):
        self.vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise', 'campbell']
        self.vendor = params.get('vendor', None)
        self.params = params
        self.resp_raw = None
        self.resp_transformed = None
        self.resp_debug = None

        self.check_params()

    def check_params(self):
        if self.vendor is None or self.vendor.lower() not in self.vendor_list:
            raise Exception('"vendor" must be specified and in the approved vendor list.')
        else:
            self.vendor = self.vendor.lower()

    def get_reading(self):
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
                self.resp_transformed = zreadings.transformed_resp
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw, dparam)
                self.resp_transformed = dreadings.transformed_resp
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
                self.resp_transformed = sreadings.transformed_resp
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
                self.resp_transformed = oreadings.transformed_resp
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
                self.resp_transformed = rreadings.transformed_resp
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
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)
                self.resp_transformed = creadings.transformed_resp 
                self.resp_debug = creadings.debug_info
            except Exception as error:
                creadings = CampbellReadings(cparam)
                self.resp_raw = Utilities.create_error_response('CAMPBELL', cparam, creadings, str(error))
                self.resp_raw = Utilities.convert_to_dict(self.resp_raw)           
            return self


def get_reading(vendor: str, **params) -> json:
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()


def get_version() -> str:
    return __version__
