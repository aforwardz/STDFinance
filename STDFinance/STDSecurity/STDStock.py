import collections
from abc import ABC
from STDFinance.STDSecurity.STDBase import STDSecurityBase


class STDStock(STDSecurityBase):
    security_type = 'stock'

    indicators = collections.OrderedDict([
        ('info', 'STDIndicatorInfo'),
    ])

    def will_load(self):
        super(STDStock, self).will_load()

    def did_load(self):
        super(STDStock, self).did_load()


