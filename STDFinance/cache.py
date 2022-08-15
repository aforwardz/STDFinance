from datetime import datetime
import requests
import redis
import traceback
import pickle
import base64
from STDFinance import conf
from STDFinance.conf import PROJECT
from STDFinance.STDUtils import log_info, log_warning, log_error, utils
import zlib
import time

__all__ = [
    'get_cache_object',
    'set_cache_object',
    "get_cache_keys",
    "clear_cache_key",
    'filter_cache_objects',
    # 'CacheAPI',
    # 'CacheORM',
    'CacheRedis',
    'get_cache_instance',
    'multiple_keys'
]


def get_cache_object(cache_key, cache_dict={}):
    if not cache_key:
        return None

    if cache_dict:
        return cache_dict.get(cache_key, None)

    from STDFinance.STDSerializer.STDSerializer import constructor

    stdcache = get_cache_instance(cache_key)
    data = stdcache.get(cache_key)
    if data:
        try:
            z_bt = base64.b64decode(data)
            if z_bt:
                bt = zlib.decompress(z_bt).decode()
                # obj = pickle.loads(bt)
                obj = constructor(bt)
                obj._cache_method = stdcache._method
                return obj
            else:
                return None
        except Exception as e:
            log_error("CONSTRUCT EXCEPTION", e)
            log_error(traceback.format_exc())
            return None
    else:
        return None


def set_cache_object(cache_key, obj):
    if not cache_key:
        return False

    from STDFinance.STDSerializer.STDSerializer import raw_serializer

    stdcache = get_cache_instance(cache_key)
    # stdcache = caches['ddcore']
    # bt = pickle.dumps(obj)
    bt = raw_serializer(obj)
    z_bt = zlib.compress(bt.encode())
    data = base64.b64encode(z_bt).decode('latin1')
    # z_data = zlib.compress(data.encode())
    stdcache.set(cache_key, data)

    return True


def clear_cache_key(cache_key):
    if not cache_key:
        return False
    stdcache = get_cache_instance(cache_key)
    stdcache.delete(cache_key)
    return True


def get_cache_keys(cache_key_pattern):
    # cache_key_pattern = product_type.id.*
    if not cache_key_pattern:
        return False
    stdcache = get_cache_instance(cache_key_pattern)
    if not stdcache:
        return False
    return stdcache.keys(cache_key_pattern)


def filter_cache_objects(cache_keys):
    t1 = time.time() * 1000000
    ret = {}
    if not cache_keys:
        return ret

    stdcache = get_cache_instance(cache_keys[0])
    cache_dict = stdcache.filter(cache_keys)
    from STDFinance.STDSerializer.STDSerializer import constructor

    for k, data in cache_dict.items():
        try:
            z_bt = base64.b64decode(data)
            if z_bt:
                bt = zlib.decompress(z_bt)
                # obj = pickle.loads(bt)
                obj = constructor(bt)
                obj._cache_method = stdcache._method
            else:
                obj = None
        except Exception as e:
            log_error("CONSTRUCT EXCEPTION", e)
            log_error(traceback.format_exc())
            obj = None
        ret[k] = obj
    t2 = time.time() * 1000000
    log_info('CACHE-FILTER', PROJECT, len(ret), stdcache._method, t2 - t1)
    return ret


def get_cache_instance(key):
    stype = key.split('.')[0]
    cache_conf = conf.get_conf(stype)['cache']
    # if cache_conf['method'] == 'ORM':
    #     return CacheORM(cache_conf['model'])
    # elif cache_conf['method'] == 'API':
    #     return CacheAPI(cache_conf['url'], cache_conf['auth'])
    if cache_conf['middleware'] == 'REDIS':
        return CacheRedis(cache_conf['address'])


def multiple_keys(product_ids, keys, product_type=""):
    if product_type:
        prefix = ['.'.join([product_type, x]) for x in product_ids]
    else:
        prefix = product_ids

    ret = []
    for pre in prefix:
        for k in keys:
            path = ".".join([pre, k])
            ret.append(path)
    return ret


class CacheRedis(object):
    _instance = {}

    def __new__(cls, url):
        if url not in cls._instance:
            cls._instance[url] = object.__new__(cls)
        return cls._instance[url]

    _method = 'Redis'

    def __init__(self, url):
        pool = redis.ConnectionPool.from_url(url, decode_responses=True)
        self.rc = redis.StrictRedis(connection_pool=pool)

    def get(self, key):
        data = self.rc.get(key)
        if data:
            return data
        return None

    def set(self, key, value):
        self.rc.set(key, value)

    def delete(self, key):
        self.rc.delete(key)

    def keys(self, pattern=None):
        if pattern:
            return self.rc.keys(pattern)
        return self.rc.keys()

    # get multiple keys
    def filter(self, keys):
        assert isinstance(keys, (list, tuple)), (
            "filter keys should be list",
        )

        ret = {}
        if not keys:
            return ret

        data_list = self.rc.mget(keys)
        for i, k in enumerate(keys):
            if data_list[i]:
                ret[k] = data_list[i]

        return ret

    def to_redis(self, keys, url):
        print(keys)
        values = self.rc.mget(keys)
        cache_redis = CacheRedis(url)
        cache_redis.rc.mset(dict(zip(keys, values)))

    # def keys(self):
    #     return self.rc.keys()


