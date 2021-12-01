import STDIndicator

__all__ = [
    'STDIndicatorInfo',
]


class STDIndicatorInfo(STDIndicator.STDIndicatorMapping):
    std_name = "info"
    std_title = "基本信息"
    _flat = True
    _prec = 4

    def load_stock(self, stdobj):
        self['name'] = ""
        self['short_name'] = ""
        self['code'] = ""
        self['ticker_symbol'] = ""
        self['exchange'] = ""

        return self
