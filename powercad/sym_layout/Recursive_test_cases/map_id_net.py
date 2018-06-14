import pandas as pd

def map_id_net(dict,symbols):
    for sym in symbols:
        for id in dict.keys():
            if sym.element.path_id==id:
                print type(sym)
                sym.net_name=dict[id]


