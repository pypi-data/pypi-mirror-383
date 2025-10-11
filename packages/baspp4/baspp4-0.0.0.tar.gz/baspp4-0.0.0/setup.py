from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("baspp4.encrypt_cython", ["baspp4/encrypt_cython.pyx"], include_dirs=["."])
]

setup(
    name="baspp4",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    packages=["baspp4"],
    package_dir={"": "."},
)

