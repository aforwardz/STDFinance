SH_EXCHANGE = ('60', '68')
SZ_EXCHANGE = ('00', '30')
BJ_EXCHANGE = ('43', '83', '87', '88')


def code_exchange_map(code: str):
    if not code:
        return None

    return 'SH' if code[:2] in SH_EXCHANGE else 'SZ' if code[:2] in SZ_EXCHANGE else 'BJ'


def code_board_map(code: str):
    if not code:
        return None

    if code.startswith('60'):
        return '沪主板'
    elif code.startswith('68'):
        return '科创板'
    elif code.startswith('00'):
        return '深主板'
    elif code.startswith('30'):
        return '创业板'
    elif code.startswith('43'):
        return '北主板-基础'
    elif code.startswith('83'):
        return '北主板-创新'
    elif code.startswith('87'):
        return '北主板-精选'
    elif code.startswith('88'):
        return '北主板-新'
    else:
        return '未知'

