from setuptools import setup, Extension
import pybind11
setup(
    name="libchessboard",
    version="0.0.1",
    setup_requires=["pybind11"],
    ext_modules=[
        Extension("libchessboard", ["chessboard.cpp"],
                  include_dirs=[pybind11.get_include()], language='c++',
                  extra_compile_args=["-std=c++17", "-fvisibility=hidden"])
    ],
    author="HamiltonHuaji",
    description="Yet Another libchessboard",
    python_requires=">=3.8",
)
