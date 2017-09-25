from bt.components.data_handler.data import TushareDataHandler
from bt.components.strategy.strategy import BuyAndHoldStrategy
from bt.components.portfolio.portfolio import NaivePortfolio
from bt.components.execution_handler.execution import SimulatedExecutionHandler

import queue
import time
import pandas as pd
import logging


pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

events = queue.Queue()
symbol_list = ["600724", "600345", "600348"]
start_datetime = "2017-09-05 00:00:00"
end_datetime = "2017-09-09 00:00:00"
data_handler = TushareDataHandler(events, symbol_list, start_datetime, end_datetime)
strategy = BuyAndHoldStrategy(data_handler, events)
portfolio = NaivePortfolio(data_handler, events, start_datetime)
broker = SimulatedExecutionHandler(events)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if data_handler.continue_backtest:
        data_handler.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    portfolio.update_timeindex()

                elif event.type == 'SIGNAL':
                    portfolio.update_from_signal(event)

                elif event.type == 'ORDER':
                    event.print_order()
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    portfolio.update_from_fill(event)

    logging.warning(portfolio.current_holdings)
    logging.warning(portfolio.current_positions)
    # logging.warning(portfolio.create_equity_curve_dataframe())

    time.sleep(5)
