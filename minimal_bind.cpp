#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

PYBIND11_MODULE(libminimal_bind, m){
    m.def("add", [](int a, int b){return a + b;});
}