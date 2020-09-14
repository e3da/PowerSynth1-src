import pickle
from powercad.general.data_struct.Abstract_Data import TestObj
import sys

def save_file(object,file):
    '''
    This function will save file in binary '*b' format
    :param file: directory and file name e.g (C:/test.txt)
    :param object: the python object to be saved
    :return: No Return, New file is created in the desired directory this is saved as a pickle binary file
    '''
    #print(file)
    pickle.dump(object, open(file, 'wb'),fix_imports=True)
    

def load_file(file):
    '''
    :param file: directory and file name e.g (C:/test.txt)
    :return: the object in pickled file whether this is unix or dos
    '''


    # python 2.x
    try:
        obj = pickle.load(open(file, 'rb'))
    except:
        data = open(file, 'rb')
        obj=pickle.load(data, fix_imports=True ,encoding="latin1")

    return obj


if __name__ == '__main__':
    print(sys.path[0])

    sel = int(input('1: to save,2 t0 load a test obj'))
    file_name =str(input('type in a file name'))
    obj = TestObj()

    if sel == 1:
        save_file(obj,file_name)
    elif sel == 2:
        obj = load_file(file_name)
        print (obj.x, obj.y)