import collections
import traceback
import copy
from typing import Any
from STDFinance import STDIndicator
from STDFinance import cache, conf
from STDFinance.conf import PROJECT
from STDIndicator import get_indicator_cls
from datetime import datetime
import time
from STDFinance.STDUtils import log_info, log_warning, log_error


class STDSecurity(object):
    security_type = "base"
    default_conf = "default"
    start_date = None  # 产品的开始时间
    est_date = None  # 具体场景的开始时间, 如组合开始时间

    indicators = collections.OrderedDict()
    keys = []  # init中传入的keys, 包括属性的keys, 如: benchmark.info, benchmark.profit
    _valid_keys = []  # 仅自己的keys, 不包括属性的keys

    _id_key = ""
    _cache_key = ""
    _force_update = False  # True:强制更新缓存
    _read_direct = False  # True:不经过缓存
    _allow_write = True  # True:允许从底层model读取
    _through = True
    _load_child = True
    pre_data = None
    tmp_entity = None

    @property
    def id_key(self):
        return self._id_key

    @classmethod
    def get_cache_key(cls, id_key=""):
        if not id_key:
            return ""
        return ".".join([cls.security_type, str(id_key)])

    @property
    def cache_key(self):
        if not self._id_key:
            return ""
        return ".".join([self.security_type, str(self._id_key)])

    def get_security(self):
        raise NotImplementedError("{} 需实现方法get_security".format(self.__class__.__name__))

    def __init__(self, id_key, **kwargs):
        '''
        @param id_key
        stock: {code}
        '''
        print('INIT STDSECURITY:', self.security_type, id_key)
        self._id_key = id_key
        self._cache_key = self.get_cache_key(id_key)

        std_conf = conf.get_conf(self.default_conf)
        self._allow_write = std_conf['allow_write'] and kwargs.get('allow_write', False)
        self._force_update = (std_conf['force_update'] or kwargs.get('force_update', False)) and self._allow_write
        self._through = kwargs.get('through', True)
        self._read_direct = kwargs.get('read_direct', False) and self._allow_write
        self._load_child = 'cache_dict' not in kwargs
        self.pre_data = kwargs.get('pre_data', {})

        self.est_date = kwargs.get('est_date')
        self.end_date = kwargs.get('end_date')

        if kwargs.get('keys') and isinstance(kwargs.get('keys'), list):
            self.keys = kwargs['keys']
            self._valid_keys = self.get_keys()
        else:
            self.keys = list(self.indicators.keys())
            self._valid_keys = self.keys
            # self._valid_keys = self.get_keys()

        if kwargs.get('tmp_entity'):
            self.tmp_entity = kwargs.get('tmp_entity')

        cache_dict = kwargs.get('cache_dict') or self.get_cache_dict()

        self.load_info(cache_dict)

        try:
            self.will_calculate()
        except Exception as e:
            log_error('STDERROR', PROJECT, self.__class__.__name__, self._id_key, "will_calculate", e)
            raise e

        self.calculate(cache_dict)

        try:
            self.did_calculate()
        except Exception as e:
            log_error('STDERROR', PROJECT, self.__class__.__name__, self._id_key, "did_calculate", e)
            raise e

    def __str__(self):
        return str(self.info)

    def get_keys(self, prefix=""):
        keys = []

        if not prefix:
            tmp_keys = set()
            for i in self.keys:
                tmp_keys.add(i)
                if i in self.indicators:
                    c = self.indicators[i]
                    cl = get_indicator_cls(c)
                    if cl:
                        # for r in cl.get_required():
                        # if r in self.indicators:
                        tmp_keys.update(cl.get_required(self.security_type))
            self.keys = list(tmp_keys)

            for i in self.keys:
                if i in self.indicators:
                    keys.append(i)
                    c = self.indicators[i]
                    cl = get_indicator_cls(c)
                    if cl:
                        for r in cl.get_required(self.security_type):
                            if r in self.indicators:
                                keys.append(r)
                elif self._load_child and '.' in i:
                    sp = i.split('.')
                    if sp[0] in self.indicators:
                        keys.append(sp[0])
        else:
            for i in self.keys:
                pre = prefix + '.'
                if i.startswith(pre):
                    keys.append(i[len(pre):])

        return list(set(keys))

    def load_info(self, cache_dict=None):
        if 'info' in self.indicators:
            vname = 'info'
            indicator_cls = self.indicators[vname]
            try:
                indicator = self.get_indicator(vname, indicator_cls, cache_dict)
                setattr(self, vname, indicator)
            except Exception as e:
                log_error('STDERROR', PROJECT, self.__class__.__name__, self._id_key, "info", e)
                raise e

            if vname in self._valid_keys:
                self._valid_keys.remove(vname)

    def will_calculate(self):
        pass

    def calculate(self, cache_dict={}):
        t1 = time.time() * 1000000

        self.__cache_dict = cache_dict
        count = 0
        for vname, indicator_cls in self.indicators.items():
            if indicator_cls and vname in self._valid_keys:
                try:
                    indicator = self.get_indicator(vname, indicator_cls, cache_dict)
                    setattr(self, vname, indicator)
                except Exception as e:
                    log_error('STDERROR', PROJECT, self.__class__.__name__, self._id_key, vname, e)
                    raise e

                count = count + 1

        t3 = time.time() * 1000000
        log_warning('TIME-PRODUCT', PROJECT, self.__class__.__name__, self._id_key, count, t3 - t1)

        return self

    def did_calculate(self):
        t1 = time.time() * 1000000
        if self.est_date:
            self.update_est()

        t2 = time.time() * 1000000
        log_info('DIDCAL', PROJECT, self.__class__.__name__, self._id_key, self._allow_write, t2 - t1)

    def update_est(self):
        pass

    # cahce handler
    def get_indicator(self, vname, indicator_cls, cache_dict={}, **kwargs):
        t1 = time.time() * 1000000
        get_method = "FUNC"
        if not indicator_cls:
            return None
        # 如果是写在product下的 get_xxx函数 直接调用
        if hasattr(self, indicator_cls):
            t12 = time.time() * 1000000
            indicator = getattr(self, indicator_cls)()
            t2 = time.time() * 1000000
            log_info('TIME-INDICATOR', PROJECT, get_method, self.__class__.__name__, self._id_key, vname, indicator_cls,
                     t2 - t1, t2 - t12)
            return indicator

        cache_key = self.get_indicator_cache_key(vname)
        cl = get_indicator_cls(indicator_cls)
        indicator = None
        cache_exist = True
        get_method = "CACHE"
        if not (self._read_direct or self._force_update or cl._never_cache):
            indicator = cache.get_cache_object(cache_key, cache_dict)
            if indicator is None or not isinstance(indicator, cl):
                cache_exist = False
            elif indicator:
                get_method = "CACHE-" + indicator._cache_method

        if not self._allow_write and not cl._lazy_load:
            t2 = time.time() * 1000000
            log_info('TIME-INDICATOR', PROJECT, get_method, self.__class__.__name__, self._id_key, vname, indicator_cls,
                     t2 - t1)
            return indicator

        if indicator is None:
            get_method = 'EVAL'
            indicator = cl(self, **kwargs)

        if not cl._never_cache and (self._force_update or not cache_exist):
            self.set_cache(vname, indicator)

        t2 = time.time() * 1000000
        log_info('TIME-INDICATOR', PROJECT, get_method, self.__class__.__name__, self._id_key, vname, indicator_cls,
                 t2 - t1)
        return indicator

    def get_indicator_cache_key(self, vname):
        if not vname:
            return ""
        return ".".join([self._cache_key, vname])

    def set_cache(self, vname, indicator=None):
        indicator = indicator if indicator is not None else getattr(self, vname)
        if indicator is None:
            return
        indicator._cache_time = time.time()
        cache_key = self.get_indicator_cache_key(vname)
        if not cache_key:
            return
        cache.set_cache_object(cache_key, indicator)

    def flush_cache(self, vnames):
        for vname in vnames:
            self.set_cache(vname)

    def clear_cache(self, vnames):
        for vname in vnames:
            cache.clear_cache_key(vname)

    def exist_cache(self):
        cache_key_pattern = "{}.*".format(self._cache_key)
        return cache.get_cache_keys(cache_key_pattern)

    def get_cache_dict(self):
        # print('get cahce dict', self.security_type)
        if self._force_update:
            return {}
        cache_keys = [self.get_indicator_cache_key('info')]
        for vname in self._valid_keys:
            cache_keys.append(self.get_indicator_cache_key(vname))
        cache_dict = cache.filter_cache_objects(cache_keys)
        return cache_dict

    def haskey(self, key):
        result = hasattr(self, key)
        if result:
            attr = getattr(self, key)
            if isinstance(attr, DDIndicator.DDIndicatorBase):
                result = result and attr and not attr.empty
        return result

    def getfrom(self, keys):
        result = None
        for k in keys:
            has = hasattr(self, k)
            if has:
                result = getattr(self, k)
                break
        return result


