import tushare as ts
from abc import ABCMeta, abstractmethod
import queue

from bt.components.event.event import MarketEvent


class DataHandler(metaclass=ABCMeta):
    """
    DataHandler是一个抽象类，它为它的很多子类提供了抽象的接口，这样做是为了让回测和在线交易复用同一套代码
    它将在每个heart beat从数据源获取一条数据，并且产生一个MarketEvent
    bars的格式是：Open-Low-High-Close-Volume-OpenInterest
    """
    def __init__(self, events: queue.Queue, symbol_list, start_datetime, end_datetime):
        self.events = events
        self.symbol_list = symbol_list
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        self.latest_symbol_data = {}
        self.symbol_data = {}
        self.continue_backtest = True
        self.get_data_from_external()

    @abstractmethod
    def get_data_from_external(self):
        raise NotImplementedError("Should implement get_data_from_external(self)")

    def get_new_bar(self, symbol):
        """
        返回一个生成器，可以用这个生成器每次获取一条数据
        :param symbol:
        :return:
        """
        for (index, row) in self.symbol_data[symbol]:
            yield tuple([symbol, index, row["open"], row["low"],
                         row["high"], row["close"], row["volume"]])

    def get_latest_bars(self, symbol, n=1) -> list:
        """
        这个方法将会从latest_symbol list中返回最新的n个bars
        :param symbol:  交易品种的代码
        :param n:   要返回的bars的个数
        :return:    所请求的bars的个数
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("get_latest_bars：给定的symbol不存在！")
        else:
            return bar_list[-n:]

    def update_bars(self):
        """
        将每个symbol的最新的bars放置到latest symbol结构中
        :return:
        """
        for s in self.symbol_list:
            try:
                new_bar = self.get_new_bar(s).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if new_bar is not None:
                    self.latest_symbol_data[s].append(new_bar)
        self.events.put(MarketEvent())


class TushareDataHandler(DataHandler):
    def __init__(self, events: queue.Queue, symbol_list, start_datetime, end_datetime):
        super(TushareDataHandler, self).__init__(events, symbol_list, start_datetime, end_datetime)

    def get_data_from_external(self):
        self.get_data_from_tushare()

    def get_data_from_tushare(self):
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = ts.get_hist_data(s, start=self.start_datetime,
                                                   end=self.end_datetime, ktype="15")
            self.symbol_data[s].sort_index(inplace=True)
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index = comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method="pad").iterrows()


