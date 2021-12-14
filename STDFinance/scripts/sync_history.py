import argparse
import akshare as ak
import baostock as bs

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


def fetch_stock_info(id_key):
    ex, raw_id = get_raw_id_key(sec_type, id_key)
    if ex == 'SH':
        return {}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync History Data.')
    parser.add_argument("--sec_type", type=str, default='all')
    parser.add_argument("--sec_id", type=str)

    args = parser.parse_args()

    sec_type = args.sec_type
    sec_id = args.sec_id

    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 获取证券基本资料
    rs = bs.query_stock_basic(code="sh.600000")
    # rs = bs.query_stock_basic(code_name="浦发银行")  # 支持模糊查询
    print('query_stock_basic respond error_code:' + rs.error_code)
    print('query_stock_basic respond  error_msg:' + rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)


