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


class SignalEvent(Event):
    """
    它是来自strategy的event，将要被portfolio接受，portfolio会在之上做出反应
    """

    def __init__(self, symbol, datetime, signal_type):
        """
        初始化SignalEvent
        :param symbol:  交易品种的代码
        :param datetime:    生成这个Signal Event的时间
        :param signal_type: 这个参数的可选有"SHORT"和"LONG"
        """
        self.type = "SIGNAL"
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type


class OrderEvent(Event):
    """
    OrderEvent将被发送给execution handler处理
    """

    def __init__(self, symbol, quantity, direction, order_type):
        """
        初始化OrderEvent
        :param symbol:  交易品种的代码
        :param quantity:    交易的数量
        :param direction:   交易的方向，可选的有"BUY"和"SELL"
        :param order_type:  订单的类型，可选的有："MKT"，表示Market；"LMT"：表示Limit
        """
        self.type = "ORDER"
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.order_type = order_type

    def print_order(self):
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % (self.symbol, self.type,
                                                                        self.quantity, self.direction))


class FillEvent(Event):
    """
    一个FillEvent里面包含了这个订单被执行之后的详细信息，包括佣金，交易数量什么的
    """
    def __init__(self, time_index, symbol, exchange, quantity, direction, fill_cost, commission=None):
        """
        初始化
        :param time_index:  The bar-resolution when the order was filled.
        :param symbol:      交易品种的代码
        :param exchange:    交易所
        :param quantity:    交易的量
        :param direction:   交易的方向，可选的有："BUY"和"SELL"
        :param fill_cost:   交易后的持仓
        :param commission:  An optional commission sent from IB.
        """
        self.type = "FILL"
        self.time_index = time_index
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # 计算佣金
        if commission is None:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission

    def calculate_commission(self):
        """
        计算交易的佣金
        :return: 计算出来的此次交易所需花费的佣金
        """
        commission_fee_rate = 0.0002
        full_cost = self.quantity * commission_fee_rate
        if full_cost <= 5:
            full_cost = 5
        return full_cost
