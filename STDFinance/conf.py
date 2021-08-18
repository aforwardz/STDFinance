
PROJECT = 'STDFinance'


STDFINANCE_CONF = {
    "default": {
        "allow_write": True,
        "force_update": False,
        "cache": {
            "middleware": "REDIS",
            "address": "redis://127.0.0.1:6379/1"
        }
    }
}


def get_conf(sec_type):
    return STDFINANCE_CONF.get(sec_type, STDFINANCE_CONF["default"])

