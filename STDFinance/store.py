from STDFinance.STDSecurity import STDStock


code = 'SH600519'

keys = ['info']

STDStock(code, allow_write=True, force_update=True, keys=keys)

