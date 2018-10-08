try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from Cython.Distutils import build_ext
import numpy

from Cython.Build import cythonize
setup(
    include_dirs=[numpy.get_include()],
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize("mutual_inductance.pyx")
)