from bt.components.event.event import MarketEvent, SignalEvent
from bt.components.data_handler.data import TushareDataHandler
from bt.components.strategy.strategy import BuyAndHoldStrategy
from bt.components.portfolio.portfolio import NaivePortfolio

from queue import Queue


duilei = Queue()
data_handler = TushareDataHandler(duilei, ["600724", "600348"], "2017-09-11", "2017-09-12")
data_handler.update_bars()
data_handler.update_bars()
data_handler.update_bars()

strategy = BuyAndHoldStrategy(data_handler, duilei)
strategy.calculate_signals(data_handler.events.get())


np = NaivePortfolio(data_handler, duilei, "2017-09-11")
nnn = np.create_equity_curve_dataframe()
print(nnn)
print(np.all_holdings)
print(duilei.queue)

duilei.get()
duilei.get()
print(duilei.queue)
np.update_from_signal(duilei.get())
duilei.get()
duilei.get().print_order()
print(duilei.queue)



