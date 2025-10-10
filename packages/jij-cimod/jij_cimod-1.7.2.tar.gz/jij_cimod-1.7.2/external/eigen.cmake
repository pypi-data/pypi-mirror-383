# Copyright 2020-2025 Jij Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

include(FetchContent)

message(CHECK_START "Fetching Eigen3")
list(APPEND CMAKE_MESSAGE_INDENT "  ")

set(FETCHCONTENT_QUIET OFF)

set(BUILD_TESTING OFF) 
set(TEST_LIB OFF)

set(EIGEN_MPL2_ONLY ON CACHE BOOL "" FORCE)
set(EIGEN_BUILD_PKGCONFIG OFF CACHE BOOL "" FORCE)
set(EIGEN_BUILD_DOC OFF CACHE BOOL "" FORCE)
set(EIGEN_DOC_USE_MATHJAX OFF CACHE BOOL "" FORCE)
set(EIGEN_BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(EIGEN_TEST_NOQT OFF CACHE BOOL "" FORCE)
set(EIGEN_LEAVE_TEST_IN_ALL_TARGET OFF CACHE BOOL "" FORCE)
#set(EIGEN_BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)

# Disable installation of Eigen3 headers to prevent them from being included in the wheel
set(EIGEN_INSTALL_HEADERS OFF CACHE BOOL "" FORCE)

if(MSVC)
  set(EIGEN_Fortran_COMPILER_WORKS OFF CACHE BOOL "" FORCE)
endif()

if(BLAS_FOUND) 
  set(EIGEN_USE_BLAS ON) 
endif()

if(LAPACK_FOUND) 
  set(EIGEN_USE_LAPACKE ON)
endif()

#### Eigen ####
FetchContent_Declare(
    eigen
    GIT_REPOSITORY  https://gitlab.com/libeigen/eigen
    GIT_TAG         3.4.1
    GIT_SHALLOW     TRUE
    )

# Prevent Eigen from being installed by using FetchContent_Populate + add_subdirectory with EXCLUDE_FROM_ALL
FetchContent_GetProperties(eigen)
if(NOT eigen_POPULATED)
    FetchContent_Populate(eigen)
    add_subdirectory(${eigen_SOURCE_DIR} ${eigen_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

add_library(cimod-eigen_lib INTERFACE)
target_include_directories(cimod-eigen_lib INTERFACE ${eigen_SOURCE_DIR})
target_compile_definitions(cimod-eigen_lib INTERFACE 
    EIGEN_MPL2_ONLY
    BUILD_TESTING=OFF
    TEST_LIB=OFF
    EIGEN_BUILD_PKGCONFIG=OFF
    EIGEN_BUILD_DOC=OFF
    EIGEN_DOC_USE_MATHJAX=OFF 
    EIGEN_BUILD_TESTING=OFF 
    EIGEN_TEST_NOQT=OFF 
    EIGEN_LEAVE_TEST_IN_ALL_TARGET=OFF 
    $<$<TARGET_EXISTS:BLAS::BLAS>:EIGEN_USE_BLAS>
    $<$<TARGET_EXISTS:LAPACK::LAPACK>:EIGEN_USE_LAPACKE>
    $<$<CXX_COMPILER_ID:MSVC>:EIGEN_Fortran_COMPILER_WORKS=OFF>
)
  

list(POP_BACK CMAKE_MESSAGE_INDENT)
message(CHECK_PASS "fetched")
