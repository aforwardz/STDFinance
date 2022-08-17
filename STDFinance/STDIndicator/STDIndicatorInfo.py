from STDFinance.STDIndicator.STDIndicatorType import *
from STDFinance.STDUtils.knowledge import code_exchange_map, code_board_map

__all__ = [
    'STDIndicatorInfo',
]


class STDIndicatorInfo(STDIndicatorMapping):
    std_name = "info"
    std_title = "基本信息"
    _flat = True
    _prec = 4

    def load_stock(self, stdobj):
        id_key = stdobj.id_key
        exchange = code_exchange_map(id_key)
        symbol = "{}.{}".format(exchange.lower(), id_key)

        bs.login()
        rs = bs.query_stock_basic(code=symbol)
        info = rs.get_row_data()
        print(info)
        info = info if info else [symbol, '', '', '', '0', '2']
        bs.logout()

        self['sec_type'] = {'1': '股票', '2': '指数', '3': '其它', '4': '可转债', '5': 'ETF', '0': '未知'}.get(info[4])
        self['name'] = info[1]
        self['short_name'] = info[1]
        self['code'] = id_key      # 600519
        self['ticker_symbol'] = symbol    # sh.600519
        self['exchange'] = exchange       # SH、SZ、BJ
        self['list_board'] = code_board_map(id_key)       #
        self['list_date'] = info[2]
        self['list_status'] = {'0': '退市', '1': '上市', '2': '未知'}.get(info[-1])
        self['delist_date'] = info[3] or None

        return self
