import collections
from abc import ABC
from STDSecurity import STDSecurity


class STDStock(STDSecurity):
    security_type = 'stock'

    indicators = collections.OrderedDict([
        ('info', 'STDIndicatorInfo'),
    ])

    def will_load(self):
        super(STDStock, self).will_load()

    def did_load(self):
        super(STDStock, self).did_load()


