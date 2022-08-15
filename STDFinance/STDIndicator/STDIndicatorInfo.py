from STDFinance import STDIndicator

__all__ = [
    'STDIndicatorInfo',
]


class STDIndicatorInfo(STDIndicator.STDIndicatorMapping):
    std_name = "info"
    std_title = "基本信息"
    _flat = True
    _prec = 4

    def load_stock(self, stdobj):
        self['sec_type'] = ""
        self['name'] = ""
        self['short_name'] = ""
        self['code'] = ""      # 600519
        self['ticker_symbol'] = ""    # 600519SH
        self['exchange'] = ""       # SH、SZ、BJ
        self['list_board'] = ""       #
        self['list_date'] = None
        self['list_status'] = ""
        self['delist_date'] = None

        return self
