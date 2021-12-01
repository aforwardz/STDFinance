import STDIndicator


def get_indicator_cls(indicator_cls):
    for indicators in [STDIndicator]:
        indicator = getattr(indicators, indicator_cls, None)
        if indicator:
            return indicator
    return None
