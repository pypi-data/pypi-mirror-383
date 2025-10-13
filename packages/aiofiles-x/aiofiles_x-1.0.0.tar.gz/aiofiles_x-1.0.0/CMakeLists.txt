# Aiofiles-X Copyright (C) 2025 ohmyarthur
#
# This file is part of <https://github.com/ohmyarthur/aiofiles-x/> Please read
# the GNU Affero General Public License in
# <https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.

cmake_minimum_required(VERSION 3.15)
project(
  aiofiles-x
  VERSION 1.0.0
  LANGUAGES CXX)

# C++20 standard (more compatible than C++23)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Position independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build options
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)
option(BUILD_GO_BINDINGS "Build Go bindings" OFF)
option(BUILD_C_BINDINGS "Build C bindings" OFF)
option(BUILD_TESTS "Build tests" ON)
option(BUILD_BENCHMARKS "Build benchmarks" ON)

# Core library (header-only)
add_library(aiofiles-core INTERFACE)
target_include_directories(
  aiofiles-core
  INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/core>
            $<INSTALL_INTERFACE:include>)

# Python bindings
if(BUILD_PYTHON_BINDINGS)
  # More flexible Python finding for CI environments
  if(PYTHON_EXECUTABLE)
    set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
  endif()

  find_package(
    Python3
    COMPONENTS Interpreter Development.Module
    REQUIRED)

  # Try to find pybind11
  find_package(pybind11 CONFIG)

  if(NOT pybind11_FOUND)
    # Download pybind11 if not found
    include(FetchContent)
    FetchContent_Declare(
      pybind11
      GIT_REPOSITORY https://github.com/pybind/pybind11
      GIT_TAG v2.11.1)
    FetchContent_MakeAvailable(pybind11)
  endif()

  pybind11_add_module(_aiofiles_core src/python/bindings.cpp)
  target_link_libraries(_aiofiles_core PRIVATE aiofiles-core)

  # Platform-specific settings
  if(WIN32)
    target_compile_definitions(_aiofiles_core PRIVATE _CRT_SECURE_NO_WARNINGS)
  elseif(APPLE)
    # macOS deployment target for std::optional compatibility
    if(NOT CMAKE_OSX_DEPLOYMENT_TARGET)
      set(CMAKE_OSX_DEPLOYMENT_TARGET
          "10.13"
          CACHE STRING "macOS deployment target")
    endif()
    # Fix macOS architecture issues
    if(CMAKE_OSX_ARCHITECTURES)
      set_target_properties(
        _aiofiles_core PROPERTIES OSX_ARCHITECTURES
                                  "${CMAKE_OSX_ARCHITECTURES}")
    endif()
  elseif(UNIX)
    # Linux-specific fixes
    target_compile_options(_aiofiles_core PRIVATE -fPIC)
  endif()
endif()

# Tests
if(BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()

# Installation
if(BUILD_PYTHON_BINDINGS)
  install(
    TARGETS _aiofiles_core
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .)
endif()
