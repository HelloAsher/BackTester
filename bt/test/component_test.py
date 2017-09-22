from queue import Queue


nn = Queue()
nn.put("sdfsadf1")
nn.put("sdfsadf2")
nn.put("sdfsadf3")
nn.put("sdfsadf4")
print(nn.get())
print(nn.get())
print(nn.get())
print(nn.get())
print(nn.get(False))
