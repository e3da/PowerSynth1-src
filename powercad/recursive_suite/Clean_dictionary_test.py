import types
from pympler import muppy,summary
import gc
from memory_profiler import profile

class obj:
    @profile
    def __init__(self):
        self.dict =None # store objects

@profile
def test():
    for i in range(10):
        ob =obj()
        new_dict ={i:"asdasdsadasdasdsadsadsadsad"}
        ob.dict=new_dict

    #new_dict =None
    #ob.dict =None
test()

