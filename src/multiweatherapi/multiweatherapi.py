import json
from os import getenv
from dotenv import load_dotenv
from os.path import isfile, isdir, join
from datetime import datetime, timezone, timedelta

from .davis import DavisParam, DavisReadings
from .spectrum import SpectrumParam, SpectrumReadings
from .zentra import ZentraParam, ZentraReadings
from .onset import OnsetParam, OnsetReadings
from .rainwise import RainwiseParam, RainwiseReadings
from .campbell import CampbellParam, CampbellReadings

__version__ = '0.0.20'


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
            zparam = ZentraParam(sn=self.params.get('sn', None),
                                 token=self.params.get('token', None),
                                 start_datetime=self.params.get('start_datetime', None),
                                 end_datetime=self.params.get('end_datetime', None),
                                 start_mrid=self.params.get('start_mrid', None),
                                 end_mrid=self.params.get('end_mrid', None),
                                 tz=self.params.get('tz', None),
                                 binding_ver=__version__)
            zreadings = ZentraReadings(zparam)
            self.resp_raw = zreadings.response
            self.resp_transformed = zreadings.transformed_resp
            self.resp_debug = zreadings.debug_info
            return self
        elif self.vendor == 'davis':
            dparam = DavisParam(sn=self.params.get('sn', None),
                                apikey=self.params.get('apikey', None),
                                apisec=self.params.get('apisec', None),
                                start_datetime=self.params.get('start_datetime', None),
                                end_datetime=self.params.get('end_datetime', None),
                                tz=self.params.get('tz', None),
                                binding_ver=__version__)
            dreadings = DavisReadings(dparam)
            self.resp_raw = dreadings.response
            self.resp_transformed = dreadings.transformed_resp
            self.resp_debug = dreadings.debug_info
            return self
        elif self.vendor == 'spectrum':
            sparam = SpectrumParam(sn=self.params.get('sn', None),
                                   apikey=self.params.get('apikey', None),
                                   start_datetime=self.params.get('start_datetime', None),
                                   end_datetime=self.params.get('end_datetime', None),
                                   date=self.params.get('date', None),
                                   tz=self.params.get('tz', None),
                                   count=self.params.get('count', None),
                                   binding_ver=__version__)
            sreadings = SpectrumReadings(sparam)
            self.resp_raw = sreadings.response
            self.resp_transformed = sreadings.transformed_resp
            self.resp_debug = sreadings.debug_info
            return self
        elif self.vendor == 'onset':
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
            oreadings = OnsetReadings(oparam)
            self.resp_raw = oreadings.response
            self.resp_transformed = oreadings.transformed_resp
            self.resp_debug = oreadings.debug_info
            return self
        elif self.vendor == 'rainwise':
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
            rreadings = RainwiseReadings(rparam)
            self.resp_raw = rreadings.response
            self.resp_transformed = rreadings.transformed_resp
            self.resp_debug = rreadings.debug_info
            return self
        elif self.vendor == 'campbell':
            cparam = CampbellParam(username=self.params.get('username', None),
                                   user_passwd=self.params.get('user_passwd', None),
                                   station_id=self.params.get('station_id', None),
                                   station_lid=self.params.get('station_lid', None),
                                   start_datetime=self.params.get('start_datetime', None),
                                   end_datetime=self.params.get('end_datetime', None),
                                   tz=self.params.get('tz', None),
                                   binding_ver=__version__)
            creadings = CampbellReadings(cparam)
            self.resp_raw = creadings.response
            self.resp_transformed = creadings.transformed_resp
            self.resp_debug = creadings.debug_info
            return self


def get_reading(vendor: str, **params) -> json:
    params['vendor'] = vendor
    return ApiWrapper(params).get_reading()


def get_version() -> str:
    return __version__


def get_sample_reports(out_dir, start_datetime=None, end_datetime=None):
    # if not env_file or not isfile(env_file):
    #     raise Exception("key file must be specified and/or key file does not exist")
    load_dotenv()
    if not out_dir or not isdir(out_dir):
        raise Exception("out_dir must be specified and/or out_dir folder does not exist")
    if start_datetime and not isinstance(start_datetime, datetime):
        raise Exception('start_datetime must be datetime.datetime instance')
    if end_datetime and not isinstance(end_datetime, datetime):
        raise Exception('end_datetime must be datetime.datetime instance')
    if start_datetime and end_datetime and (start_datetime > end_datetime):
        raise Exception('start_datetime must be earlier than end_datetime')
    if not start_datetime or not end_datetime:
        start_datetime = datetime.now() - timedelta(hours=24)
        end_datetime = start_datetime + timedelta(hours=2)

    def gen_report(vendor):
        params = json.loads(getenv(vendor.upper()))
        params['start_datetime'] = start_datetime
        params['end_datetime'] = end_datetime
        resp = get_reading(vendor, **params)
        with open(join(out_dir, vendor+'.json'), 'w') as wf:
            json.dump(resp.resp_raw, wf, indent=2)
        print(resp.resp_raw)

    # Campbell - Good
    gen_report('campbell')

    # Davis - Good
    gen_report('davis')

    # Onset - Good
    gen_report('onset')

    # Rainwise - Warning
    gen_report('rainwise')

    # Spectrum - Good
    gen_report('spectrum')

    # Zentra - Good
    gen_report('zentra')
