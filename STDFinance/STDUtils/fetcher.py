import akshare as ak

__all__ = ['fetch_data']

allow_indicators = ('info',)


def get_raw_id_key(sec_type, id_key):
    if sec_type == 'stock':
        if id_key.startswith('SH'):
            return 'SH', id_key.lstrip('SH')
        elif id_key.startswith('SZ'):
            return 'SZ', id_key.lstrip('SZ')

    return sec_type, id_key


def fetch_data(sec_type, indicator, id_key, **kwargs):
    if not all([sec_type, indicator, id_key]):
        raise ValueError
    if indicator not in allow_indicators:
        raise KeyError('Indicator %s is Not Exists or Allowed' % indicator)

    fetch_method = 'fetch_{}_{}'.format(sec_type, indicator)

    ak_data = fetch_ak_data(fetch_method, **kwargs)

    return fetch_method(ak_data, id_key, **kwargs)


def fetch_ak_data(method, **kwargs):
    if method == 'fetch_stock_info':
        return


def fetch_stock_info(raw_data, sec_type, id_key):
    ex, raw_id = get_raw_id_key(sec_type, id_key)
    if ex == 'SH':
        return {}
