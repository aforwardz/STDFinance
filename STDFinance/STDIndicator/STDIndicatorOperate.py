from STDFinance.STDIndicator.STDIndicatorType import *

__all__ = [
    'STDIndicatorMainOperate',
]


class STDIndicatorMainOperate(STDIndicatorSequence):
    std_name = "main_operate"
    std_title = "主营业务"

    _attribute_mapping = {}

    def load_stock(self, stdobj):
        df = ak.stock_zygc_ym(symbol=stdobj.info['code'])

        df = df.sort_values('报告期')

