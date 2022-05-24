## conftest.py  
# test configuration.  This is run before running any of the test files

import pytest, os

# read in the .env file at the root of the project for all tests
from dotenv import load_dotenv
load_dotenv()

# allow command line option pytest --vendor RAINWISE for example
# if none sent, run for all vendors

def pytest_addoption(parser):
    parser.addoption( "--vendor", action="store", default=None,
     help='a specific vendor to test.  Default = all')


def pytest_generate_tests(metafunc):
    """parameterize command line options to inject into every test, specifically vendor
    If a vendor is passed on command line, use that, else use all vendors"""
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".

    vendor_option = metafunc.config.getoption("vendor") 
    all_vendors = ['DAVIS', 'CAMPBELL', 'ONSET', 'RAINWISE', 'SPECTRUM', 'ZENTRA'] 
    #   NOTE zentra is removed because can only check once per 60s.   

    # for those tests that require a vendor... check for param and also for config
    if "vendor" in metafunc.fixturenames:
        if vendor_option is not None:
            vendors_to_test = [vendor_option.upper()]      
            # metafunc.parametrize('vendor', [vendor_option.upper()])
        else:
            vendors_to_test = all_vendors
            # metafunc.parametrize('vendor', all_vendors)
        
        # only thest those vendors for which we have config loaded in the environment
        # that could be none!
        vendors_in_config = [v for v in vendors_to_test if v.upper() in os.environ.keys()]
        metafunc.parametrize('vendor', vendors_in_config)


