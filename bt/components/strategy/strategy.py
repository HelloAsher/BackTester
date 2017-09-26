from abc import ABCMeta, abstractmethod
import queue

from bt.components.event.event import SignalEvent, MarketEvent
from bt.components.data_handler.data import DataHandler


class Strategy(metaclass=ABCMeta):
    """
    1、这是所有strategy类的父类，定义了统一的方法
    2、这个类的作用是根据市场数据（MarketEvent），为特定的股票生成SignalEvent；
    3、这个方法可以适用于历史数据，也可以用于在线实时交易系统
    4、strategy类接受MarketEvent，然后生成SignalEvent
    """

    def __init__(self, data_handler: DataHandler, events: queue.Queue):
        """
        用来初始化BuyAndHoldStrategy这个类的
        :param data_handler:    DataHandler类的实例
        :param events:  消息队列
        """
        self.data_handler = data_handler
        self.symbol_list = self.data_handler.symbol_list
        self.events = events

        self.bought = {symbol: False for symbol in self.symbol_list}

    @abstractmethod
    def calculate_signals(self, event: MarketEvent):
        """
        提供计算signal的原型，其计算结果就是生成一个个的OrderEvent
        :return:
        """
        raise NotImplementedError("Should implement calculate_signals()")


class BuyAndHoldStrategy(Strategy):
    """
    1、这个类是最简单的类，策略就是买并且一直持有某只股票
    2、作用是：这个策略所持有的股票可以作为benchmark，用来跟其他策略做比较
    """

    def __init__(self, data_handler: DataHandler, events: queue.Queue):
        """
        用来初始化BuyAndHoldStrategy这个类的
        :param data_handler:    DataHandler类的实例
        :param events:  消息队列
        """
        super(BuyAndHoldStrategy, self).__init__(data_handler, events)

    def calculate_signals(self, event: MarketEvent):
        """
        在BuyAndHoldStrategy中，为每一个symbol产生一个买signal，这意味着我们长久持有symbol_list中的股票
        :param event:   MarketEvent
        :return:
        """
        if event.type == "MARKET":
            for s in self.symbol_list:
                bar = self.data_handler.get_latest_bars(s)
                if bar is not None and bar != []:
                    if self.bought[s] is False:
                        signal = SignalEvent(bar[0][0], bar[0][1], "LONG", 10)
                        self.events.put(signal)
                        self.bought[s] = True
        pass
