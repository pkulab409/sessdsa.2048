from setuptools import setup, find_packages, Extension
import pybind11
setup(
    name="libchessboard",
    version="0.0.1",
    packages=find_packages(),
    setup_requires=["pybind11"],
    ext_modules=[
        Extension("libchessboard", ["chessboard.cpp"],
                  include_dirs=[pybind11.get_include()], language='c++',
                  extra_compile_args=["-std=c++17"])
    ],
    author="HamiltonHuaji",
    description="Yet Another libchessboard",
    python_requires=">=3.8",
)
