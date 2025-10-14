cmake_minimum_required(VERSION 3.15)
project(shmx_python)

# Require C++17 minimum for pybind11
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find or fetch pybind11 - it will handle Python detection automatically
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    message(STATUS "pybind11 not found, fetching from GitHub...")
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# pybind11 already found Python for us, no need for find_package(Python)
# It sets up all necessary Python variables automatically

# Include parent project headers (support both development and packaged source)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../src")
    # Development build - headers are in parent src directory
    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/..)
    message(STATUS "Using headers from: ${CMAKE_CURRENT_SOURCE_DIR}/../src")
elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src")
    # Packaged build - headers are in local src directory
    include_directories(${CMAKE_CURRENT_SOURCE_DIR})
    message(STATUS "Using headers from: ${CMAKE_CURRENT_SOURCE_DIR}/src")
else()
    message(FATAL_ERROR "Cannot find src directory with headers. Checked:\n"
            "  ${CMAKE_CURRENT_SOURCE_DIR}/../src\n"
            "  ${CMAKE_CURRENT_SOURCE_DIR}/src")
endif()

# Create Python module using pybind11
pybind11_add_module(shmx_core MODULE shmx_py.cpp)

# Set output name and location
set_target_properties(shmx_core PROPERTIES
    OUTPUT_NAME "shmx_core"
)

# Platform-specific settings
if(MSVC)
    target_compile_options(shmx_core PRIVATE /W4 /permissive-)
    target_compile_definitions(shmx_core PRIVATE _CRT_SECURE_NO_WARNINGS)
else()
    target_compile_options(shmx_core PRIVATE -Wall -Wextra -Wpedantic)
    # On Linux, link against rt library for shm_open/shm_unlink
    if(UNIX AND NOT APPLE)
        target_link_libraries(shmx_core PRIVATE rt pthread)
    endif()
endif()

# Install rules
install(TARGETS shmx_core LIBRARY DESTINATION shmx)
