cmake_minimum_required(VERSION 3.0.0)
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/toolchain.cmake")
project (libchessboard)

message(STATUS "If you can't find python3, include python3 include path manually")
set(Python3_USE_STATIC_LIBS FALSE)
find_package(Python3 COMPONENTS Development REQUIRED)
if(Python3_FOUND)
    include_directories(${Python3_INCLUDE_DIRS})
    link_libraries(${Python3_LIBRARIES})
endif()

find_package(pybind11 REQUIRED)
if(pybind11_FOUND)
    include_directories(${Pybind11_INCLUDE_DIRS})
    link_libraries(${Pybind11_LIBRARIES})
endif()


find_package(fmt REQUIRED)
include_directories(Fmt_INCLUDE_DIRS)
link_libraries(fmt)

add_compile_options(-O3)
add_compile_options(-funroll-loops)
add_compile_options(-ffast-math)
add_compile_options(-static)
add_compile_options(-Wfatal-errors)

add_library(
    chessboard
    SHARED
    ${CMAKE_SOURCE_DIR}/chessboard.cpp
)
add_definitions(-D FOR_PYTHON37_AND_PYTHON36)
add_library(
    chessboard7
    SHARED
    ${CMAKE_SOURCE_DIR}/chessboard.cpp
)