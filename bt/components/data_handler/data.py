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
