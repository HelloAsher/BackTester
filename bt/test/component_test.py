from queue import Queue
from bt.components.event.event import MarketEvent, SignalEvent

nn = Queue()
nn.put("sdfsadf1")
nn.put("sdfsadf2")
nn.put("sdfsadf3")
nn.put("sdfsadf4")
print(nn.get())
print(nn.get())
print(nn.get())
print(nn.get())
# print(nn.get(False))

import pandas as pd

ddd = pd.Series(data=[1, 1.8, 1.2, 1, 0.5])
tt = ddd.pct_change()
fff = (1.0 + tt).cumprod()
print(tt)
print(fff)


ssss = ddd.cumprod()
print(ssss)


print(MarketEvent().type_enum)
print(SignalEvent("sdf", "dafs", "fdsa", 12).type_enum)
print("sadfas", MarketEvent().type_enum == SignalEvent("sdf", "dafs", "fdsa", 12).type_enum)


import tushare as ts


sadfasd = ts.bar("600348", start_date="2017-09-01 09:30:00", end_date="2017-09-06 15:00:00", ktype="60min")
sadfasd.sort_index(inplace=True)
# sadfasd = ts.get_k_data("600724", "2017-09-05", "2017-09-07", ktype="60")
# sadfasd = ts.get_k_data("600724")
print(sadfasd)