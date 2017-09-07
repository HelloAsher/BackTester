from abc import ABCMeta, abstractmethod
import pandas as pd
import datetime
import os, os.path
from bt.components.event.event import MarketEvent


class DataHandler(metaclass=ABCMeta):
    """
    DataHandler是一个抽象类，它为它的很多子类提供了抽象的接口，这样做是为了让回测和在线交易复用同一套代码
    它将在每个heart beat从数据源获取一条数据，并且产生一个MarketEvent
    bars的格式是：Open-Low-High-Close-Volume-OpenInterest
    """

    @abstractmethod
    def get_latest_bars(self, symbol, n=1):
        """
        这个方法将会从latest_symbol list中返回最新的n个bars
        :param symbol:  交易品种的代码
        :param n:   要返回的bars的个数
        :return:    所请求的bars的个数
        """
        raise NotImplementedError("get_latest_bars没有被实例化！")

    @abstractmethod
    def update_bars(self):
        """
        将每个symbol的最新的bars放置到latest symbol结构中
        :return:
        """
        raise NotImplementedError("update_bars没有被实例化！")


class HistoricCSVDataHandler(DataHandler):
    """
    这个类是用来读取CSV文件中的数据的，并且会产生MarketEvent
    """

    def __init__(self, events, csv_path, symbol_list):
        """
        初始化这个DataHandler，将CSV数据和股票代码数据装载到内存
        :param events:  events是一个queue，这里面装的是很多的event
        :param csv_path:    这个代表的是csv文件的决定路径
        :param symbol_list: 指代的是股票代码的list
        """
        self.events = events
        self.csv_dir = csv_path
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        从csv文件中将数据读取出来，并且按照一定的格式组织成dataframe
        symbol_data中存放的格式是：symbol_data{"symbol": [(index, row), (index, row)]}
        :return:
        """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.read_csv(os.path.join(self.csv_dir, "%s.csv" % s), header=0, index_col=0,
                                              names=['datetime', 'open', 'low', 'high', 'close', 'volume', 'oi'])
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index = comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method="pad").iterrows()

    def _get_bew_bar(self, symbol):
        """
        用来获取最新的bar，格式是：(sybmbol, datetime, open, low, high, close, volume)
        tips：从这个函数可以看出bar其实就是一个list，这个list中存放的是某只股票的各个日期的的详细信息
        :param symbol:  交易品种的代码
        :return:    一个generator
        """
        for (index, row) in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.datetime.strftime(index, "%Y-%m-%d %H:%M:%S"), row[0], row[1], row[2],
                         row[3, row[4]]])

    def get_latest_bars(self, symbol, n=1):
        """
        用来获取某只股票最新的N条信息
        :param symbol:  交易品种的代码
        :param n:   获取最新的多少个信息
        :return:    返回的bar
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("get_latest_bars：给定的symbol不存在！")
        else:
            return bar_list[-n:]

    def update_bars(self):
        """
        将latest_bar放到latest_symbol_data中，并且产生一个MarketEvent，然后将这MarketEvent放到queue中
        :return:
        """
        for s in self.symbol_list:
            try:
                bar = self._get_bew_bar(symbol=s).__next__
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent)
