import pickle


def save_file(object,file):
    '''
    This function will save file in binary '*b' format
    :param file: directory and file name e.g (C:/test.txt)
    :param object: the python object to be saved
    :return: No Return, New file is created in the desired directory this is saved as a pickle binary file
    '''
    print file
    pickle.dump(object, open(file, 'wb'))

def load_file(file):
    '''
    :param file: directory and file name e.g (C:/test.txt)
    :return: the object in pickled file whether this is unix or dos
    '''

    try:
        obj = pickle.load(open(file, 'rb'))
    except:
        obj = pickle.load(open(file, 'rU'))
    return obj
