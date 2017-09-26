from queue import Queue
from bt.components.event.event import MarketEvent

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


print(MarketEvent().type)