from distutils.core import setup
from Cython.Build import cythonize
import sys

setup(
    ext_modules=cythonize("cy_pg.pyx"),
)
