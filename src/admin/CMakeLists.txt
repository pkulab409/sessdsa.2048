cmake_minimum_required(VERSION 3.0.0)
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/toolchain.cmake")
project (libchessboard)

set(Boost_PYTHON_VERSION 3.8)
set(Python3_USE_STATIC_LIBS FALSE)
find_package(Python3 COMPONENTS Development REQUIRED)
if(Python3_FOUND)
    include_directories(${Python3_INCLUDE_DIRS})
    link_libraries(${Python3_LIBRARIES})
endif()
find_package(Boost COMPONENTS filesystem iostreams serialization python REQUIRED)
if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
    link_libraries(${Boost_LIBRARIES})
endif()

if(MSVC)
    message(STATUS "f**k MSVC")
    message(STATUS "not adapted yet.")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS "ON")
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

find_package(fmt REQUIRED)
include_directories(Fmt_INCLUDE_DIRS)
link_libraries(fmt)

add_compile_options(-fPIC)
add_compile_options(-O3)
add_compile_options(-funroll-loops)
add_compile_options(-ffast-math)
add_compile_options(-static)
add_library(
    chessboard
    SHARED
    ${CMAKE_SOURCE_DIR}/chessboard.cpp
)
