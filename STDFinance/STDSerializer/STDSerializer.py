import collections
import decimal
import json
import pickle
import zlib
import base64
import numpy as np
import pandas as pd
from datetime import date
from STDFinance.STDIndicator import STDIndicatorType
from STDFinance.STDSecurity import *
from STDFinance.STDUtils import utils
from STDUtils.indicator import get_indicator_cls


class STDSerializerSecurity(object):
    def __init__(self, stdsecurity, **kwargs):
        super().__init__()
        self.security = stdsecurity

    def data(self):
        data = {
            'security_type': self.security.security_type,
            'stdclass': self.security.__class__.__name__,
            'id_key': self.security._id_key
        }
        if not hasattr(self.security, 'info'):
            raise Exception('security must contains info')
        if 'info' not in self.security.keys:
            data['info'] = self.security.info
        for k in self.security.keys:
            if hasattr(self.security, k):
                indicator = getattr(self.security, k)
                data[k] = indicator

        return data


class STDSerializerIndicatorBase(object):
    def __init__(self, stdindicator=None, **kwargs):
        super().__init__()
        self.indicator = stdindicator
        self._mode = kwargs.get('mode', 'raw')

    def get_basic_representation(self):
        ret = {}
        ret['std_class'] = self.indicator.__class__.__name__
        ret['std_name'] = self.indicator.std_name
        ret['std_title'] = self.indicator.std_title
        ret['help_text'] = self.indicator.help_text
        ret['value'] = utils.value_format(self.indicator.value, self.indicator._prec)

        ret['summary_text'] = self.indicator.summary_text
        ret['start_date'] = utils.date_format(self.indicator.start_date)
        ret['end_date'] = utils.date_format(self.indicator.end_date)
        ret['duration'] = self.indicator.duration
        ret['duration_text'] = utils.duration_format(self.indicator.duration)
        if self.indicator.rank_text:
            ret['rank_text'] = self.indicator.rank_text
        if self.indicator.rank_pos:
            ret['rank_pos'] = self.indicator.rank_pos
            ret['rank_pct'] = self.indicator.rank_pct
            ret['rank_review'] = self.indicator.rank_review
        return ret

    def to_representation(self):
        return self.indicator.__dict__

    @property
    def sdata(self):
        return self.to_representation()


class STDSerializerIndicatorSingle(STDSerializerIndicatorBase):

    def to_representation(self):
        data = self.get_basic_representation()
        data["base_indicator"] = "STDIndicatorSingle"
        return data


class STDSerializerIndicatorMapping(STDSerializerIndicatorBase):
    def to_representation(self):
        data = self.get_basic_representation()
        data.update({"base_indicator": "STDIndicatorMapping", "mapping": self.indicator.data})
        return data


# class DDSerializerIndicatorInfo(DDSerializerIndicatorMapping):
#     def to_representation(self):
#         data = {}
#         fields = self.get_fields()
#         for k, v in fields.items():
#             data[k] = self.get_value(v)
#         return data


class STDSerializerIndicatorSequence(STDSerializerIndicatorBase):
    def to_representation(self):
        data = self.get_basic_representation()
        data.update({"base_indicator": "STDIndicatorSequence", "sequence": list(self.indicator)})

        return data


def serialize_df(df):
    bt = pickle.dumps(df)
    z_bt = zlib.compress(bt)
    df = base64.b64encode(z_bt).decode('latin1')

    return df


def deserialize_df(df):
    z_bt = base64.b64decode(df)
    bt = zlib.decompress(z_bt)
    df = pickle.loads(bt)

    return df


class STDSerializerIndicatorDataFrame(STDSerializerIndicatorBase):
    def to_representation(self):
        data = self.get_basic_representation()
        df = serialize_df(self.indicator.df)
        data.update({"base_indicator": "STDIndicatorDataFrame",
                     "df": df if self._mode != 'standard' else df.reset_index().astype({'date': str, 'value': float}).to_dict('records')})

        return data


class DDRawEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, STDSecurity):
            v = STDSerializerSecurity(obj).data()
        elif isinstance(obj, STDIndicatorType.STDIndicatorSingle):
            v = STDSerializerIndicatorSingle(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorMapping):
            v = STDSerializerIndicatorMapping(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorSequence):
            v = STDSerializerIndicatorSequence(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorDataFrame):
            v = STDSerializerIndicatorDataFrame(obj).sdata
        elif isinstance(obj, decimal.Decimal):
            v = float(obj)
        elif isinstance(obj, pd.DataFrame):
            v = {'raw_df': serialize_df(obj)}
        elif isinstance(obj, (np.int32, np.int64)):
            v = int(obj)
        elif isinstance(obj, date):
            v = {'date_type': utils.date_format(obj)}
        elif isinstance(obj, datetime):
            v = {'time_type': utils.date_format(obj, '%Y-%m-%d %H:%M:%S')}
        elif np.isnan(obj):
            v = None
        else:
            return json.JSONEncoder.default(self, obj)

        return v


class DDStandardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, STDSecurity):
            v = STDSerializerSecurity(obj).data()
        elif isinstance(obj, STDIndicatorType.STDIndicatorSingle):
            v = STDSerializerIndicatorSingle(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorMapping):
            v = STDSerializerIndicatorMapping(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorSequence):
            v = STDSerializerIndicatorSequence(obj).sdata
        elif isinstance(obj, STDIndicatorType.STDIndicatorDataFrame):
            v = STDSerializerIndicatorDataFrame(obj, mode='standard').sdata
        elif isinstance(obj, decimal.Decimal):
            v = float(obj)
        elif isinstance(obj, pd.DataFrame):
            df = serialize_df(obj)
            v = df.reset_index().astype({'date': str, 'value': float}).to_dict('records')
        elif isinstance(obj, (np.int32, np.int64)):
            v = int(obj)
        elif isinstance(obj, date):
            v = utils.date_format(obj)
        elif isinstance(obj, datetime):
            v = utils.date_format(obj, '%Y-%m-%d %H:%M:%S')
        elif np.isnan(obj):
            v = None
        else:
            return json.JSONEncoder.default(self, obj)

        return v


class STDRSerializer(object):
    _string = ""
    _json = {}
    _mode = ''

    def __init__(self, mode='raw'):
        self._mode = mode

    def serialize(self, ddobj):
        return json.dumps(ddobj, cls=DDRawEncoder if self._mode != 'standard' else DDStandardEncoder)

    def __call__(self, ddobj):
        return self.serialize(ddobj)


raw_serializer = STDRSerializer()
standard_serializer = STDRSerializer(mode='standard')


class STDConstructor(object):
    security = None

    def _construct_security(self, data):
        security_type = data.get('security_type')
        sec_cls = SECURITY_TYPES.get(security_type)
        assert sec_cls, "STDSecurity %s Class Not Found" % security_type

        security = sec_cls.__new__(sec_cls)
        security._id_key = data.pop('id_key')

        if not data.get('info'):
            raise Exception('DDEntity Must Contain Info')
        info = data.pop('info')
        setattr(security, 'info', self._construct_indicator(info))

        _valid_fields = set(security.indicators.keys())

        for k, v in data.items():
            if k in _valid_fields:
                security.keys.append(k)
                setattr(security, k, self._construct_indicator(v))
            else:
                setattr(security, k, v)

        return security

    def _construct_indicator(self, data):
        if not isinstance(data, dict):
            return data
        if isinstance(data, dict) and data.get('security_type'):
            return self._construct_security(data)
        elif isinstance(data, dict) and data.get('base_indicator'):
            base_indicator = data.pop('base_indicator')
            indicator_cls = data.get('std_class')
            indicator = get_indicator_cls(indicator_cls)
            assert indicator, "STDIndicator %s Class Not Found" % indicator_cls
            # indicator = indicator.__new__(indicator)
            indicator = indicator()
            if base_indicator == 'STDIndicatorSingle':
                for k, v in data.items():
                    setattr(indicator, k, v)
            elif base_indicator == 'STDIndicatorMapping':
                indicator.data = {}
                mapping = data.pop('mapping')
                for k, v in mapping.items():
                    indicator[k] = self._construct_indicator(v)
            elif base_indicator == 'STDIndicatorSequence':
                indicator.data = []
                sequence = data.pop('sequence')
                indicator.extend([self._construct_indicator(i) for i in sequence])
            elif base_indicator == 'STDIndicatorDataFrame':
                df = deserialize_df(data.pop('df'))
                indicator.df = df

            for k, v in data.items():
                setattr(indicator, k, v)

            return indicator
        elif isinstance(data, dict) and data.get('raw_df') is not None:
            df = deserialize_df(data.get('raw_df'))
            return df
        elif isinstance(data, dict) and data.get('date_type') is not None:
            return datetime.strptime(data.get('date_type'), '%Y-%m-%d').date() if data.get('date_type') else data.get('date_type')
        elif isinstance(data, dict) and data.get('time_type') is not None:
            return datetime.strptime(data.get('time_type'), '%Y-%m-%d %H:%M:%S') if data.get('time_type') else data.get('time_type')
        elif isinstance(data, dict):
            return dict((k, self._construct_indicator(v)) for k, v in data.items())
        else:
            return data

    def _construct(self, data):
        self._construct_security(data)
        if not data.get('info'):
            raise Exception('STDSecurity Must Contain Info')
        info = data.pop('info')
        setattr(self.security, 'info', self._construct_indicator(info))

        _valid_fields = set(self.security.indicators.keys())
        print(_valid_fields)

        for k, v in data.items():
            if k in _valid_fields:
                self.security.keys.append(k)
                setattr(self.security, k, self._construct_indicator(v))
            else:
                setattr(self.security, k, v)

        return self.security

    def __call__(self, json_string):
        data = json.loads(json_string)
        return self._construct_indicator(data)


constructor = STDConstructor()

