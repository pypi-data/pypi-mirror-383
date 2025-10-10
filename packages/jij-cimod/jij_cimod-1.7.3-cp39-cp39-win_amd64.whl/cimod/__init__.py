# Copyright 2020-2025 Jij Inc.


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'jij_cimod.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-jij_cimod-1.7.3')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-jij_cimod-1.7.3')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from cimod import cxxcimod

from cimod.model.binary_polynomial_model import (
    BinaryPolynomialModel,
    make_BinaryPolynomialModel,
    make_BinaryPolynomialModel_from_JSON,
)
from cimod.model.binary_quadratic_model import (
    BinaryQuadraticModel,
    make_BinaryQuadraticModel,
    make_BinaryQuadraticModel_from_JSON,
)
from cimod.vartype import BINARY, SPIN, Vartype

__all__ = [
    "cxxcimod",
    "SPIN",
    "BINARY",
    "Vartype",
    "make_BinaryQuadraticModel",
    "make_BinaryQuadraticModel_from_JSON",
    "BinaryQuadraticModel",
    "make_BinaryPolynomialModel",
    "make_BinaryPolynomialModel_from_JSON",
    "BinaryPolynomialModel",
]
