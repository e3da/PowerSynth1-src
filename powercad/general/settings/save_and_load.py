import pickle
from powercad.project_builder.project import Project


def save_file(obj, filename):
    """
    This function will save file in binary '*b' format
    :param filename: directory and file name e.g (C:/test.txt)
    :param obj: the python object to be saved
    :return: No Return, New file is created in the desired directory this is saved as a pickle binary file
    """
    print file

    # This block checks to see if there is a running MATLAB engine in the project then closes and sets it to None
    # before saving the project file.
    if isinstance(obj, Project):
        perf_measures = obj.symb_layout.perf_measures
        from powercad.sym_layout.symbolic_layout import ThermalMeasure
        for measure in perf_measures:
            if isinstance(measure, ThermalMeasure):
                if hasattr(measure, 'matlab_engine'):
                    measure.matlab_engine.quit()
                    measure.matlab_engine = None

    pickle.dump(obj, open(filename, 'wb'))


def load_file(filename):
    """
    :param filename: directory and file name e.g (C:/test.txt)
    :return: the object in pickled file whether this is unix or dos
    """

    try:
        obj = pickle.load(open(filename, 'rb'))
    except:
        obj = pickle.load(open(filename, 'rU'))

    # Similar to above, this block restarts the MATLAB engine if it was used in a previously saved project.
    if isinstance(obj, Project):
        perf_measures = obj.symb_layout.perf_measures
        from powercad.sym_layout.symbolic_layout import ThermalMeasure
        for measure in perf_measures:
            if isinstance(measure, ThermalMeasure):
                if hasattr(measure, 'matlab_engine'):
                    from powercad.general.settings.settings import MATLAB_PATH
                    import matlab.engine
                    measure.matlab_engine = matlab.engine.start_matlab()
                    measure.matlab_engine.cd(MATLAB_PATH)

    return obj

