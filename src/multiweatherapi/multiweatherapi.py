import json
from .davis import DavisParam, DavisReadings
from .spectrum import SpectrumParam, SpectrumReadings
from .zentra import ZentraParam, ZentraReadings
from .onset import OnsetParam, OnsetReadings


class ApiWrapper:
    def __init__(self, params: dict):
        self.vendor_list = ['zentra', 'spectrum', 'davis', 'onset', 'rainwise']
        self.vendor = params.get('vendor', None)
        self.params = params
        self.resp_raw = None
        self.resp_parsed = None

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
                                 end_mrid=self.params.get('end_mrid', None))
            zreadings = ZentraReadings(zparam)
            self.resp_raw = zreadings.response
            self.resp_parsed = zreadings.parsed_resp
            return self
        elif self.vendor == 'davis':
            dparam = DavisParam(sn=self.params.get('sn', None),
                                apikey=self.params.get('apikey', None),
                                apisec=self.params.get('apisec', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None))
            dreadings = DavisReadings(dparam)
            self.resp_raw = dreadings.response
            self.resp_parsed = dreadings.parsed_resp
            return self
        elif self.vendor == 'spectrum':
            sparam = SpectrumParam(sn=self.params.get('sn', None),
                                   apikey=self.params.get('apikey', None),
                                   start_date=self.params.get('start_date', None),
                                   end_date=self.params.get('end_date', None),
                                   date=self.params.get('date', None),
                                   count=self.params.get('count', None))
            sreadings = SpectrumReadings(sparam)
            self.resp_raw = sreadings.response
            self.resp_parsed = sreadings.parsed_resp
            return self
        elif self.vendor == 'onset':
            oparam = OnsetParam(sn=self.params.get('sn', None),
                                client_id=self.params.get('client_id', None),
                                client_secret=self.params.get('client_secret', None),
                                ret_form=self.params.get('ret_form', None),
                                user_id=self.params.get('user_id', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None))
            oreadings = OnsetReadings(oparam)
            self.resp_raw = oreadings.response
            self.resp_parsed = oreadings.parsed_resp
            return self


def get_reading(vendor: str, **params) -> json:
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()
