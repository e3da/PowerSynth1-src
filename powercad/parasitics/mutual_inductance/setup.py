try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from Cython.Distutils import build_ext
from Cython.Build import cythonize
from distutils.extension import Extension
import numpy

ext_modules = [
    Extension(
        "mutual_inductance",
        ["mutual_inductance.pyx"],
        extra_compile_args=['/openmp'],
        extra_link_args=['/openmp'],
    )
]

''' python setup.py build_ext --inplace '''
setup(
    name="multithreads_mutual",
    include_dirs=[numpy.get_include()],
    #cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(ext_modules)

)