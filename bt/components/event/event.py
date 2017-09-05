class Event(object):
    """
    Event类是为其子类提供接口的
    """
    pass


class MarketEvent(Event):
    """
    用来驱动市场数据的更新
    """
    def __init__(self):
        self.type = "MARKET"
