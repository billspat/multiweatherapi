import json
from .davis import DavisParam, DavisReadings
from .spectrum import SpectrumParam, SpectrumReadings
from .zentra import ZentraParam, ZentraReadings
from .onset import OnsetParam, OnsetReadings
from .rainwise import RainwiseParam, RainwiseReadings
from .campbell import CampbellParam, CampbellReadings

__version__ = '0.0.16'


class ApiWrapper:
    def __init__(self, params: dict):
        self.vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise', 'campbell']
        self.vendor = params.get('vendor', None)
        self.params = params
        self.resp_raw = None
        self.resp_parsed = None
        self.resp_debug = None

        self.check_params()

    def check_params(self):
        if self.vendor is None or self.vendor.lower() not in self.vendor_list:
            raise Exception('"vendor" must be specified and in the approved vendor list.')

    def get_reading(self):
        if self.vendor == 'zentra':
            zparam = ZentraParam(sn=self.params.get('sn', None),
                                 token=self.params.get('token', None),
                                 start_date=self.params.get('start_date', None),
                                 end_date=self.params.get('end_date', None),
                                 start_mrid=self.params.get('start_mrid', None),
                                 end_mrid=self.params.get('end_mrid', None),
                                 binding_ver=__version__)
            zreadings = ZentraReadings(zparam)
            self.resp_raw = zreadings.response
            self.resp_parsed = zreadings.parsed_resp
            self.resp_debug = zreadings.debug_info
            return self
        elif self.vendor == 'davis':
            dparam = DavisParam(sn=self.params.get('sn', None),
                                apikey=self.params.get('apikey', None),
                                apisec=self.params.get('apisec', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None),
                                binding_ver=__version__)
            dreadings = DavisReadings(dparam)
            self.resp_raw = dreadings.response
            self.resp_parsed = dreadings.parsed_resp
            self.resp_debug = dreadings.debug_info
            return self
        elif self.vendor == 'spectrum':
            sparam = SpectrumParam(sn=self.params.get('sn', None),
                                   apikey=self.params.get('apikey', None),
                                   start_date=self.params.get('start_date', None),
                                   end_date=self.params.get('end_date', None),
                                   date=self.params.get('date', None),
                                   count=self.params.get('count', None),
                                   binding_ver=__version__)
            sreadings = SpectrumReadings(sparam)
            self.resp_raw = sreadings.response
            self.resp_parsed = sreadings.parsed_resp
            self.resp_debug = sreadings.debug_info
            return self
        elif self.vendor == 'onset':
            oparam = OnsetParam(sn=self.params.get('sn', None),
                                client_id=self.params.get('client_id', None),
                                client_secret=self.params.get('client_secret', None),
                                ret_form=self.params.get('ret_form', None),
                                user_id=self.params.get('user_id', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None),
                                binding_ver=__version__)
            oreadings = OnsetReadings(oparam)
            self.resp_raw = oreadings.response
            self.resp_parsed = oreadings.parsed_resp
            self.resp_debug = oreadings.debug_info
            return self
        elif self.vendor == 'rainwise':
            rparam = RainwiseParam(username=self.params.get('username', None),
                                   sid=self.params.get('sid', None),
                                   pid=self.params.get('pid', None),
                                   mac=self.params.get('mac', None),
                                   ret_form=self.params.get('ret_form', None),
                                   interval=self.params.get('interval', None),
                                   start_date=self.params.get('start_date', None),
                                   end_date=self.params.get('end_date', None),
                                   binding_ver=__version__)
            rreadings = RainwiseReadings(rparam)
            self.resp_raw = rreadings.response
            self.resp_parsed = rreadings.parsed_resp
            self.resp_debug = rreadings.debug_info
            return self
        elif self.vendor == 'campbell':
            cparam = CampbellParam(username=self.params.get('username', None),
                                   user_passwd=self.params.get('user_passwd', None),
                                   station_id=self.params.get('station_id', None),
                                   station_lid=self.params.get('station_lid', None),
                                   start_date=self.params.get('start_date', None),
                                   end_date=self.params.get('end_date', None),
                                   binding_ver=__version__)
            creadings = CampbellReadings(cparam)
            self.resp_raw = creadings.response
            self.resp_parsed = creadings.parsed_resp
            self.resp_debug = creadings.debug_info
            return self


def get_reading(vendor: str, **params) -> json:
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()


def get_version() -> str:
    return __version__
