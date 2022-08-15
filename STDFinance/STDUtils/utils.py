from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from decimal import Decimal
from STDFinance.STDUtils.options import DURATION_MAPPING
import io
import importlib
import pandas as pd
import decimal


def decimal2float(dec, division=None, precision=2):
    if dec is None:
        # prina('No Chanae')
        return dec
    else:
        try:
            dec = float(dec)
        except Exception as _:
            return dec
        if division and division != 0:
            dec = dec / division
        if precision:
            dec = round(dec, precision)
        return dec


def get_lowercase_underscore_name(text):
    lst = []
    for index, char in enumerate(text):
        if char.isupper() and index != 0:
            lst.append("_")
        lst.append(char)

    return "".join(lst).lower()


def get_start_end(end_date, duration, record_df=None, limit_start_date=None):
    duration_delta = {
        '1D': relativedelta(days=1),
        '1W': relativedelta(weeks=1),
        '1M': relativedelta(months=1),
        '3M': relativedelta(months=3),
        '6M': relativedelta(months=6),
        '1Y': relativedelta(years=1),
        '2Y': relativedelta(years=2),
        '3Y': relativedelta(years=3),
        '5Y': relativedelta(years=5),
        '10Y': relativedelta(years=10),
    }
    start_date = None
    if duration == 'YTD':
        year = end_date.year
        start_date = date(year, 1, 1) - relativedelta(days=1)
    elif duration == 'MTD':
        year = end_date.year
        month = end_date.month
        start_date = date(year, month, 1) - relativedelta(days=1)
    elif duration == 'WTD':
        wd = end_date.weekday()
        start_date = end_date - relativedelta(days=wd) - relativedelta(days=1)
    elif duration == 'QTD':
        start_date, _ = season_start_end(end_date)
        start_date = start_date - relativedelta(days=1)
    elif duration in duration_delta:
        start_date = end_date - duration_delta[duration]

    if record_df is None or record_df.empty:
        return start_date, end_date, True

    if duration == 'EST':
        start_date = record_df.iloc[0].name
    elif start_date:
        sub = record_df[:start_date]
        if sub.empty:
            # start_date = None
            pass
        else:
            start_date = sub.iloc[-1].name

    is_full = start_date and start_date >= record_df.iloc[0].name

    if not start_date or start_date < record_df.iloc[0].name:
        start_date = record_df.iloc[0].name

    if limit_start_date and start_date < limit_start_date:
        start_date = record_df[limit_start_date:].iloc[0].name

    return start_date, end_date, is_full


def get_window(duration):
    duration_delta = {
        "1M": 1,
        "3M": 2,
        "6M": 3,
        "YTD": 4,
        "1Y": 5,
        "2Y": 6,
        "3Y": 7,
        "EST": 8,
    }

    return duration_delta.get(duration)


def get_season(current_date):
    return int((current_date.month - 1) / 3) + 1


def season_start_end(current_date=None, year=None, season=None):
    if not year or not season:
        year = current_date.year
        season = get_season(current_date)
    if season == 1:
        start_date = date(year, 1, 1)
        end_date = date(year, 3, 31)
    elif season == 2:
        start_date = date(year, 4, 1)
        end_date = date(year, 6, 30)
    elif season == 3:
        start_date = date(year, 7, 1)
        end_date = date(year, 9, 30)
    else:
        start_date = date(year, 10, 1)
        end_date = date(year, 12, 31)

    return start_date, end_date


# range_type: MONTH|SEASON|YEAR


def period_start_end(current_date, range_type="MONTH"):
    y, m, d = current_date.year, current_date.month, current_date
    if range_type == 'MONTH':
        sd = date(y, m, 1)
        nxt = current_date + relativedelta(months=1)
        nxt_sd = date(nxt.year, nxt.month, 1)
        ed = nxt_sd - relativedelta(days=1)
        return sd, ed

    elif range_type == 'SEASON':
        return season_start_end(current_date)

    elif range_type == 'YEAR':
        sd = date(y, 1, 1)
        ed = date(y, 12, 31)
        return sd, ed


# fmt: DAY|MONTH|SEASON|YEAR


def date_format(d, fmt="DAY", style=""):
    if not d:
        return ""
    if not isinstance(d, (datetime, date)):
        return d
    if fmt == 'DAY':
        return d.strftime("%Y-%m-%d")
    elif fmt == 'MONTH':
        return d.strftime("%Y-%m")
    elif fmt == 'SEASON':
        season = get_season(d)
        if style == "zh":
            return "%d年%d季度" % (d.year, season)
        return "%dQ%d" % (d.year, season)
    elif fmt == 'YEAR':
        return str(d.year)


def duration_format(k):
    return DURATION_MAPPING.get(k) or ""


def value_format(num, prec=2):
    if isinstance(num, (Decimal, float)):
        if prec is not None:
            return float(round(num, prec))
        return float(num)
    return num


def get_pre_half_year_report_date(report_date):
    if report_date.month == 6 and report_date.day == 30:
        return date(report_date.year - 1, 12, 31)
    elif report_date.month == 12 and report_date.day == 31:
        return date(report_date.year, 6, 30)
    else:
        raise ('invalid report_date')


def last_quarter(n=1, index=0, delay=False, now=None):
    if not isinstance(n, int):
        raise TypeError('n should be Int type')
    lst = [
        ('-03-31', '第一季度报', '年一季度'),
        ('-06-30', '第二季度报', '年二季度'),
        ('-09-30', '第三季度报', '年三季度'),
        ('-12-31', '第四季度报', '年四季度')]
    if not now or type(now) != date:
        now = datetime.now()
    if delay:
        now = now - timedelta(days=30)
    cur_season = (now.month - 1) // 3
    d, m = divmod(n, 4)
    last_season = (cur_season - m - 1) % 4  # 对应lst索引
    last_year = now.year - (d + 1 if m >= cur_season else 0)
    return "{year}{month_day}".format(year=last_year, month_day=lst[last_season][index])


def generate_seasons(start_date, end_date):
    """
    生成start_date 与 end_date 范围内的所有完整的季度
    """
    season_pairs = [([1, 1], [3, 31]), ([4, 1], [6, 30]),
                    ([7, 1], [9, 30]), ([10, 1], [12, 31])]
    start_year = start_date.year
    end_year = end_date.year
    for year in range(start_year, end_year + 1):
        for season_start, season_end in season_pairs:
            season_start_date = date(year, season_start[0], season_start[1])
            if season_start_date < start_date:
                continue
            season_end_date = date(year, season_end[0], season_end[1])
            if season_end_date > end_date:
                continue
            yield (season_start_date, season_end_date)


def generate_months(start_date, end_date):
    """
    生成start_date 与 end_date 范围内的所有完整的月份
    """
    if start_date.day == 1:
        month_start = date(start_date.year, start_date.month, 1)
    else:
        month_start = (start_date + relativedelta(months=1)).replace(day=1)
        # month_start = date(start_date.year, start_date.month + 1, 1)
    month_end = month_start + relativedelta(months=1) - relativedelta(days=1)
    while month_end <= end_date:
        yield month_start, month_end
        month_start = month_start + relativedelta(months=1)
        month_end = month_start + \
                    relativedelta(months=1) - relativedelta(days=1)


def generate_years(start_date, end_date):
    """
    生成start_date 与 end_date 范围内的所有完整的月份
    """
    sy = start_date.year + 1
    ey = end_date.year - 1
    while sy <= ey:
        yield date(sy, 1, 1), date(sy, 12, 31)
        sy = sy + 1


def generate_period(start_date, end_date, range_type="MONTH"):
    if range_type == 'MONTH':
        return generate_months(start_date, end_date)
    elif range_type == 'SEASON':
        return generate_seasons(start_date, end_date)
    elif range_type == 'YEAR':
        return generate_years(start_date, end_date)


def generate_period_for_limit(end_date, range_type="MONTH", limit=12):
    if range_type == 'MONTH':
        return generate_months_for_limit(end_date, limit=limit)
    elif range_type == 'SEASON':
        return generate_seasons_for_limit(end_date, limit=limit)
    elif range_type == 'YEAR':
        return generate_years_for_limit(end_date, limit=limit)


def generate_months_for_limit(end_date, limit=12):
    month_end = end_date.replace(day=1) - timedelta(days=1)
    month_start = month_end.replace(day=1)
    while limit > 0:
        yield month_start, month_end
        month_end = month_start - timedelta(days=1)
        month_start = month_end.replace(day=1)
        limit -= 1


def generate_seasons_for_limit(end_date, limit=12):
    season_pairs = [([1, 1], [3, 31]), ([4, 1], [6, 30]),
                    ([7, 1], [9, 30]), ([10, 1], [12, 31])]

    season_index = ((end_date.month - 1) // 3) - 1
    temp = 3 - season_index
    while limit > 0:
        season_start_pair, season_end_pair = season_pairs[season_index]
        year = end_date.year - temp // 4
        yield date(year, *season_start_pair), date(year, *season_end_pair)
        temp += 1
        season_index = (season_index - 1) % 4
        limit -= 1


def generate_years_for_limit(end_date, limit=12):
    year = end_date.year - 1
    while limit > 0:
        yield date(year, 1, 1), date(year, 12, 31)
        year -= 1
        limit -= 1


def get_nearest_value(df, the_date, step, max_step=15):
    if step.days > 0:
        if not df[df.index >= the_date].empty:
            return df[df.index >= the_date].iloc[0].value
    else:
        if not df[df.index <= the_date].empty:
            return df[df.index <= the_date].iloc[-1].value
    return None


def f2s(num, sign=True, pct=False, n=2):
    """float格式化为str"""
    if num is None:
        return "--"
    with_sign = ''
    if sign and num > 0:
        with_sign = '+'

    return with_sign + '%.{}f'.format(n) % round(num, n) + ('%' if pct else '')


def load_module(text):
    if "." not in text:
        return importlib.import_module(".", text)

    ll = text.split(".")
    head, tail = ".".join(ll[:-1]), ll[-1]
    n = importlib.import_module(".", head)
    return getattr(n, tail)


def df2csv(df):
    if df is None or df.empty:
        return ""
    s = io.StringIO()
    df.to_csv(s)
    text = s.getvalue()
    return text


def csv2df(text, astype):
    # text = zlib.decompress(text)
    if not text.strip():
        return None
    s = io.StringIO(text)
    df = pd.read_csv(s, index_col=0).astype(astype)

    index_name = df.index.name
    df.index = list(df.reset_index().apply(
        lambda x: datetime.strptime(x[index_name], "%Y-%m-%d").date(), axis=1))
    df.index.name = index_name
    return df


class Singleton:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance


def row2dict(obj, keys=None):
    if not keys:
        return dict(zip(obj.keys(), obj))
    res = {}
    for k in obj.keys():
        if k not in keys:
            continue
        res[k] = getattr(obj, k)
    return res


def rows2dict(qs, keys=None):
    if not keys:
        return [row2dict(obj) for obj in qs]
    return [row2dict(obj, keys) for obj in qs]


def orm_transaction(d):
    new = set()
    # TODO 从django filter 转换到sqlalchemy filter
    for key, value in d.items():
        if "__" not in key:
            new.add(column(key) == value)
        elif key.endswith("__in"):
            key = key.replace("__in", "")
            new.add(column(key).in_(value))
        elif "__icontains" in key or "__contains" in key:
            key = key.replace("__icontains", "").replace("__contains", "")
            new.add(column(key).contains(value))
        elif "__isnull" in key:
            key = key.replace("__isnull", "")
            if value:
                new.add(column(key) == None)
            else:
                new.add(column(key) != None)
    return new


def force_bytes(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    return s.encode(encoding, errors)