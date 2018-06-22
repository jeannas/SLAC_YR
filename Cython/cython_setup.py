from distutils.core import setup, Extension
from Cython.Build import cythonize

ext_type = Extension("indexamajig_complete",
                     sources=["indexamajig_complete.pyx",
                              "im-sandbox.c", "stdio.c", "index.c", "detector.c", "cell.c", "process_image.c", "stream.c"])


setup(name="indexamajig_complete",
      ext_modules = cythonize([ext_type]))
