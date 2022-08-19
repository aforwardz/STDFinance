from STDFinance.STDIndicator.STDIndicatorType import *

__all__ = [
    'STDIndicatorHistRecordsDaily',
]


def get_stock_hist(code):
    hist = ak.stock_zh_a_hist(symbol=code, period='daily')

    return hist


class STDIndicatorHistRecords(STDIndicatorDataFrame):
    std_name = "hist_records"
    std_title = "历史行情"

    _attribute_mapping = {}

    def load_stock(self, stdobj):
        self.df = get_stock_hist(stdobj.info['code'])


class STDIndicatorHistRecordsDaily(STDIndicatorHistRecords):
    std_name = "hist_records_daily"
    std_title = "日频历史行情"
    frequency = "DAY"

    def load_stock(self, stdobj):
        super(STDIndicatorHistRecordsDaily, self).load_stock(stdobj)

        return self

