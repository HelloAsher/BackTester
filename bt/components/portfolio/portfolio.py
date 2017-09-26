import pandas as pd

from abc import ABCMeta, abstractmethod
from math import floor
from queue import Queue

from bt.components.event.event import OrderEvent, FillEvent, SignalEvent
from bt.components.data_handler.data import DataHandler
from bt.components.performance.performance import create_drawdowns, create_sharp_ratio


class Portfolio(metaclass=ABCMeta):
    """
    这个类处理所有股票的持仓，处理的形式是秒级，分钟级，5分钟级，30分钟级。。。。。
    """

    def __init__(self, data_handler: DataHandler, events: Queue, start_datetime, initial_capital):
        """
        通过DataHandler（bars）和一个event queue来初始化一个NavePortfolio，还有一个开始日期
        :param data_handler:    DataHandler
        :param events:
        :param start_datetime:
        :param initial_capital:
        """
        self.data_handler = data_handler
        self.symbol_list = self.data_handler.symbol_list
        self.events: Queue = events
        self.start_datetime = start_datetime
        self.initial_capital = initial_capital

        self.all_positions = self.construct_all_positions()
        self.current_positions = {symbol: 0 for symbol in self.symbol_list}

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def construct_all_positions(self):
        dic = {symbol: 0 for symbol in self.symbol_list}
        dic["datetime"] = self.start_datetime
        return [dic]

    def construct_all_holdings(self):
        dic = {symbol: 0.0 for symbol in self.symbol_list}
        dic["datetime"] = self.start_datetime
        dic["cash"] = self.initial_capital
        dic["commission"] = 0.0
        dic["total"] = self.initial_capital
        return [dic]

    def construct_current_holdings(self):
        dic = {symbol: 0.0 for symbol in self.symbol_list}
        dic["cash"] = self.initial_capital
        dic["commission"] = 0.0
        dic["total"] = self.initial_capital
        return dic

    def update_positions_from_fill(self, fill: FillEvent):
        """
        根据FillEvent更新当前持仓信息
        :param fill:
        :return:
        """
        fill_direction = 0
        if fill.direction == "BUY":
            fill_direction = 1
        if fill.direction == "SELL":
            fill_direction = -1
        self.current_positions[fill.symbol] += fill_direction * fill.quantity
        pass

    def update_holdings_from_fill(self, fill: FillEvent):
        """
        根据FillEvent更新当前持有资金量信息
        :param fill:
        :return:
        """
        fill_direction = 0
        if fill.direction == "BUY":
            fill_direction = 1
        if fill_direction == "SELL":
            fill_direction = -1
        close_price = self.data_handler.get_latest_bars(fill.symbol)[0][5]
        cost = fill_direction * fill.quantity * close_price
        self.current_holdings[fill.symbol] += cost
        self.current_holdings["commission"] += fill.commission
        self.current_holdings["cash"] -= (cost + fill.commission)
        self.current_holdings["total"] -= (cost + fill.commission)
        pass

    def update_from_fill(self, event: FillEvent):
        if event.type == "FILL":
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
        pass

    def update_from_signal(self, event: SignalEvent):
        if event.type == "SIGNAL":
            order = self.generate_order(event)
            self.events.put(order)
        pass

    @abstractmethod
    def generate_order(self, event: SignalEvent) -> OrderEvent:
        raise NotImplementedError("Should implement generate_naive_order(self, event)")

    def update_timeindex(self):
        """
        将current_positions和current_holdings的内容追加到all_positions和all_holdings这两个list中
        :return:
        """
        latest_bar_of_every_symbol = {}
        for symbol in self.symbol_list:
            latest_bar_of_every_symbol[symbol] = self.data_handler.get_latest_bars(symbol, n=1)

        # 1、更新positions
        dic_position_new = {symbol: 0 for symbol in self.symbol_list}
        dic_position_new["datetime"] = latest_bar_of_every_symbol[self.symbol_list[0]][0][1]
        for s in self.symbol_list:
            dic_position_new[s] = self.current_positions[s]
        # 把current_positions更新到all_positions中
        self.all_positions.append(dic_position_new)

        # 2、更新holdings
        dic_holding_new = {symbol: 0.0 for symbol in self.symbol_list}
        dic_holding_new["datetime"] = latest_bar_of_every_symbol[self.symbol_list[0]][0][1]
        dic_holding_new["cash"] = self.current_holdings["cash"]
        dic_holding_new["commission"] = self.current_holdings["commission"]
        dic_holding_new["total"] = self.current_holdings["cash"]
        for s in self.symbol_list:
            market_value = self.current_positions[s] * latest_bar_of_every_symbol[s][0][5]
            dic_holding_new[s] = market_value
            dic_holding_new["total"] += market_value
        # 把current_holdings更新到all_holdings中
        self.all_holdings.append(dic_holding_new)

    def create_equity_curve_dataframe(self) -> pd.DataFrame:
        """
        根据当前持有资金量创建可以画出净值曲线的dataframe
        :return:
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index("datetime", inplace=True)
        curve["returns"] = curve["total"].pct_change()  # 计算相邻两个数之间的变化百分比，(next - pre) / pre
        curve["equity_curve"] = (1.0 + curve["returns"]).cumprod()  # 将这个数组的每个数连乘起来
        return curve

    def output_summary_stats(self):
        """
        为portfolio创建一个包含统计信息的list，包括夏普比率和最大回撤等
        :return: 一个包含了统计信息的list
        """
        equity_curve = self.create_equity_curve_dataframe()
        total_return_and_capital = equity_curve["equity_curve"][-1]
        returns = equity_curve["returns"]
        pnl = equity_curve["equity_curve"]

        sharp_ratio = create_sharp_ratio(returns)
        max_drawdown, duration = create_drawdowns(pnl)

        stats = {"total return": "%0.2f%%" % ((total_return_and_capital - 1) * 100),
                 "sharp ratio": "%0.2f" % sharp_ratio, "max drawdown": '%0.2f%%' % (max_drawdown * 100.0),
                 "drawdown duration": "%d" % duration}
        return stats


class NaivePortfolio(Portfolio):
    """
    NaivePortfolio是用来想brokerage发送OrderEvent的，只不过这个类中没有做复杂的风险控制等内容，这只是一个及其简单的版本，主要
    目的是用来测试一些简单的策略，比如BuyAndHoldStrategy这样的
    """

    def __init__(self, data_handler: DataHandler, events: Queue, start_datetime, initial_capital=100000.0):
        """
        通过DataHandler（bars）和一个event queue来初始化一个NavePortfolio，还有一个开始日期
        :param data_handler:    DataHandler
        :param events:
        :param start_datetime:
        :param initial_capital:
        """
        super(NaivePortfolio, self).__init__(data_handler, events, start_datetime, initial_capital)

    def generate_order(self, event: SignalEvent) -> OrderEvent:
        return self.generate_naive_order(event)

    def generate_naive_order(self, event: SignalEvent) -> OrderEvent:
        order = None

        symbol = event.symbol
        strength = event.strength
        direction = event.signal_type

        market_quantity = floor(100 * strength)
        current_quantity = self.current_positions[symbol]
        order_type = "MKT"
        if direction == "LONG" and current_quantity == 0:
            order = OrderEvent(symbol, market_quantity, "BUY", order_type)
        if direction == "SHORT" and current_quantity == 0:
            order = OrderEvent(symbol, market_quantity, "SELL", order_type)

        if direction == "EXIT" and current_quantity < 0:
            order = OrderEvent(symbol, market_quantity, "BUY", order_type)
        if direction == "EXIT" and current_quantity < 0:
            order = OrderEvent(symbol, market_quantity, "SELL", order_type)
        return order
        pass
