import collections
import pandas as pd
from datetime import datetime
from STDFinance.STDUtils import utils
from STDFinance.STDIndicator import get_indicator_cls


class STDIndicatorBase(object):
    _never_cache = False
    _lazy_load = False  # 注意!!! lazy_load要和never_cache一起设置, if true: never_cache=True, 且attr_mapping失效
    _cache_method = "CACHE-METHOD"
    std_name = ""
    std_title = ""
    help_text = ""
    value = None

    summary_text = ""
    summary_review = ""
    _variable_ddname = ""

    __start_date = None
    __end_date = None
    duration = ""  # 1D/1W/1M/3M/6M/1Y/2Y/3Y/5Y/YTD/EST
    frequency = ""  # DAY/MONTH/SEASON/HALYEAR
    _prec = 2
    _skip_load = False

    __rank = None
    rank_text = ""  # "90/200"
    rank_pos = None  # 90
    rank_pct = None  # 45.00 (%)
    rank_review = ""  # 一般/较差

    # _attribute_mapping = {}

    required = []

    kwargs = {}

    @classmethod
    def get_required(cls, security_type="default"):
        if cls._skip_load:
            return []
        indicator = cls()
        return indicator.required

    def __init__(self, stdobj=None, **kwargs):
        super().__init__()
        self._cache_time = None

        if self._lazy_load:
            self._never_cache = True

        self.kwargs = kwargs

        if kwargs.get('start_date'):
            self.start_date = kwargs['start_date']
        if kwargs.get('end_date'):
            self.end_date = kwargs['end_date']
        if kwargs.get("duration"):
            self.duration = kwargs["duration"]
        if kwargs.get("offset"):
            self.offset = kwargs["offset"]
        if kwargs.get("frequency"):
            self.frequency = kwargs["frequency"]

        if stdobj and not self._skip_load and not kwargs.get('skip_load'):
            self.load(stdobj)

    @property
    def cache_time(self):
        return self._cache_time and datetime.fromtimestamp(self._cache_time)

    @property
    def empty(self):
        raise ValueError
    
    @property
    def is_empty(self):
        return True

    @property
    def period(self):
        return self.start_date, self.end_date

    @property
    def trade_date(self):
        return self.__end_date

    @property
    def start_date(self):
        return self.__start_date

    @property
    def end_date(self):
        return self.__end_date

    @start_date.setter
    def start_date(self, d):
        if d and isinstance(d, str):
            self.__start_date = datetime.strptime(d, "%Y-%m-%d").date()
        else:
            self.__start_date = d

    @end_date.setter
    def end_date(self, d):
        if d and isinstance(d, str):
            self.__end_date = datetime.strptime(d, "%Y-%m-%d").date()
        else:
            self.__end_date = d

    @property
    def rank(self):
        return self.rank_text

    # @rank.setter
    # def rank(self, txt):
    #     self.rank_text = txt
    #     if self.rank_text and '/' in self.rank_text:
    #         v1, v2 = self.rank_text.split('/')
    #         if float(v2) != 0.0:
    #             self.rank_pct = round(eval(self.rank_text) * 100, 2)
    #             self.rank_pos = int(self.rank_text.split('/')[0])
    #             self.rank_review = utils.pct_text(self.rank_pct)

    # deprecated
    @property
    def variable_name(self):
        if not self._variable_name:
            cls_name = self.__class__.__name__
            if cls_name.startswith('STDIndicator'):
                cls_name = cls_name[11:]
            self._variable_name = utils.get_lowercase_underscore_name(cls_name)
        return self._variable_name

    # def calculate(self, stdobj, product=None, product_extend=None):
    #     if stdobj.security_type:
    #         func = "calculate_"+stdobj.security_type
    #         if hasattr(self, func):
    #             return getattr(self, func)(stdobj, product, product_extend)
    #         elif hasattr(self, 'calculate_'):
    #             return self.calculate_(stdobj, product, product_extend)
    #         # return eval("self.{}(stdobj, product, product_extend)".format(func))
    #     return self

    def load(self, stdobj):
        indicator = self
        if self._skip_load:
            return indicator
        if stdobj.security_type:
            return indicator
        return indicator


class STDIndicatorSingle(STDIndicatorBase):
    _prec = 2  # 精确位数
    _figure_shift = 0  # 位数, 百分数为2, 万份收益为4

    @property
    def empty(self):
        return self.value is None or self.value == ""

    def __str__(self):
        if self.start_date:
            return "{} : {}".format(self.period, self.value)
        else:
            return "{} : {}".format(self.trade_date, self.value)

    def calculate(self, stdobj):
        return super().load(stdobj)


class STDIndicatorMapping(STDIndicatorBase, collections.UserDict):
    _indicator_mapping = {}
    _flat = False

    def __getattribute__(self, name):
        if name != 'data' and name != 'self' and name.startswith('K_') and name[2:] in self:
            return self[name[2:]]
        else:
            return object.__getattribute__(self, name)

    @property
    def empty(self):
        return {}
    
    @property
    def is_empty(self):
        return not self

    @classmethod
    def get_indicator_mapping(cls, k):
        if cls._indicator_mapping:
            return cls._indicator_mapping.get(k) or cls._indicator_mapping.get('default') or {}
        return {}

    @classmethod
    def get_required(cls, security_type="default"):
        if cls._skip_load:
            return []
        indicator = cls()
        required = []
        mapping = cls.get_indicator_mapping(security_type)
        if mapping:
            for _, indicator_cls_name in mapping.items():
                indicator_cls = get_indicator_cls(indicator_cls_name)
                required.extend(indicator_cls.get_required(security_type))
        else:
            required = indicator.required
        return list(set(required))

    def load(self, stdobj):
        # self.attribute_from_mapping(stdobj, product, product_extend)
        if self._indicator_mapping:
            self.indicator_from_mapping(stdobj)
        else:
            return super().load(stdobj)

    def indicator_from_mapping(self, stdobj):
        mapping = self.get_indicator_mapping(stdobj.security_type)
        for k, indicator_cls in mapping.items():
            # exec("from . import "+in:dicator_cls)
            self[k] = get_indicator_cls(indicator_cls)(stdobj)
            # self[k] = eval(indicator_cls+'(stdobj, product, product_extend)')


class STDIndicatorMappingLazy(STDIndicatorMapping):
    _never_cache = True
    _lazy_load = True

    pretty_ddtitle_mapping = {}

    def __init__(self, stdobj=None, **kwargs):
        super().__init__(stdobj, **kwargs)
        if self._lazy_load and self._never_cache:
            self._stdobj = stdobj

    def __getitem__(self, k):
        if k in self.data or not hasattr(self, '_stdobj'):
            return self.data[k]

        mapping = self.get_indicator_mapping(self._stdobj.security_type)
        indicator_cls = mapping.get(k)
        if indicator_cls:
            self.data[k] = get_indicator_cls(indicator_cls)(self._stdobj)
        return self.data.get(k)

    def indicator_from_mapping(self, stdobj):
        mapping = self.get_indicator_mapping(stdobj.security_type)
        for k, indicator_cls in mapping.items():
            if not self._lazy_load or self._default_key == k:
                obj_vname = self.ddname + "_" + k
                if hasattr(stdobj, obj_vname):
                    self[k] = getattr(stdobj, obj_vname)
                    delattr(stdobj, obj_vname)
                else:
                    self[k] = get_indicator_cls(indicator_cls)(stdobj)

    @classmethod
    def get_pretty_ddtitle(cls, k):
        return cls.pretty_ddtitle_mapping.get(k, k)


class STDIndicatorSequence(STDIndicatorBase, collections.UserList):
    frequency = ""  # DAY|WEEK|MONTH|SEASON|YEAR

    @property
    def empty(self):
        return []

    @property
    def is_empty(self):
        return not self

    __date_index = None

    @property
    def date_index(self):
        if self.__date_index is None:
            self.__date_index = {}
            for idx, ind in enumerate(self):
                if ind.end_date:
                    self.__date_index[ind.end_date] = idx
        return self.__date_index

    def at(self, end_date):
        if end_date in self.date_index:
            idx = self.date_index[end_date]
            return self[idx]
        return None


class STDIndicatorDataFrame(STDIndicatorBase):
    frequency = ""  # DAY|WEEK|MONTH|SEASON|YEAR
    __df = None
    is_full = True  # 日期是否满

    # _csv = ""
    # astype = {"value": "float"}

    @property
    def empty(self):
        return pd.DataFrame()

    @property
    def is_empty(self):
        return self.df is None or self.df.empty

    @property
    def df(self):
        # if self.__df is None and self._csv:
        #     self.__df = utils.csv2df(self._csv, self.astype)
        #     self._csv = ""
        return self.__df

    @df.setter
    def df(self, df):
        self.__df = df

    # def to_csv(self):
    #     if self.__df is not None:
    #         self._csv = utils.df2csv(self.__df)
    #     self.__df = None



