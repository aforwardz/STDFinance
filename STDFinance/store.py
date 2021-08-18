from STDFinance.STDSecurity import STDStock


code = 'SH600519'

keys = ['info']

# st = STDStock('SH600519', allow_write=True, force_update=True, keys=['info'])

st = STDStock('SH600519', keys=['info'])
print(st, st.info)
