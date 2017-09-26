import datetime
from queue import Queue

from abc import ABCMeta, abstractclassmethod

from bt.components.event.event import OrderEvent, FillEvent, EventType


class ExecutionHandler(metaclass=ABCMeta):
    """
    ExecutionHandler是用来处理portfolio和市场数据的相互交互的，填充FillEvent
    """

    def __init__(self, events: Queue):
        self.events = events

    @abstractclassmethod
    def execute_order(self, event: OrderEvent):
        """
        消费一个OrderEvent，然后产生一个FillEvent，然后将这FillEvent放到Event Queue中
        :param event:   OrderEvent
        :return:
        """
        raise NotImplementedError("Should implement execute_order()")


class SimulatedExecutionHandler(ExecutionHandler):
    """
    1、SimulatedExecutionHandler只是把一个OrderEvent转化成了FillEvent，这只是简单的转化，本类中没有考虑延迟、滑点和填充率的问题
    2、在实现一个复杂的执行系统之前，这个简单的ExecutionHandler对任何一个策略都是到来就立即执行
    """

    def __init__(self, events: Queue):
        super(SimulatedExecutionHandler, self).__init__(events)

    def execute_order(self, event: OrderEvent):
        if event.typename == EventType.ORDER:
            fill_event = FillEvent(datetime.datetime.utcnow(), event.symbol, "SH", event.quantity, event.direction,
                                   None)
            self.events.put(fill_event)
        pass
