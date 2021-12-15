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
        self.response = None
        self.parsed_resp = None

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
            self.response = ZentraReadings(zparam).response
            return self.response
        elif self.vendor == 'davis':
            dparam = DavisParam(sn=self.params.get('sn', None),
                                apikey=self.params.get('apikey', None),
                                apisec=self.params.get('apisec', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None))
            self.response = DavisReadings(dparam).response
            return self.response
        elif self.vendor == 'spectrum':
            sparam = SpectrumParam(sn=self.params.get('sn', None),
                                   apikey=self.params.get('apikey', None),
                                   start_date=self.params.get('start_date', None),
                                   end_date=self.params.get('end_date', None),
                                   date=self.params.get('date', None),
                                   count=self.params.get('count', None))
            self.response = SpectrumReadings(sparam).response
            return self.response
        elif self.vendor == 'onset':
            oparam = OnsetParam(sn=self.params.get('sn', None),
                                client_id=self.params.get('client_id', None),
                                client_secret=self.params.get('client_secret', None),
                                ret_form=self.params.get('ret_form', None),
                                user_id=self.params.get('user_id', None),
                                start_date=self.params.get('start_date', None),
                                end_date=self.params.get('end_date', None))
            self.response = OnsetReadings(oparam).response
            return self.response


def get_reading(vendor: str, **params) -> json:
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()
