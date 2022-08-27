from STDFinance.STDIndicator.STDIndicatorType import *

__all__ = [
    'STDIndicatorDividendRecords',
]


class STDIndicatorDividendRecords(STDIndicatorDataFrame):
    std_name = "dividend_records"
    std_title = "分红记录"

    _attribute_mapping = {}

    def load_stock(self, stdobj):
        all_df = ak.stock_history_dividend()
        self.df = all_df[all_df['代码'] == stdobj.info['code']]


