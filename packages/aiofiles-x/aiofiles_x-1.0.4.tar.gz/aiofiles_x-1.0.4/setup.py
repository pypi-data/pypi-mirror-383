#!/usr/bin/env python3
"""
Setup script for aiofiles-x.

This builds the C++ extension module using pybind11.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """CMake extension."""

    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Build extension using CMake."""

    def build_extension(self, ext):
        """Build the extension."""
        if not isinstance(ext, CMakeExtension):
            super().build_extension(ext)
            return

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            "-DBUILD_PYTHON_BINDINGS=ON",
            "-DBUILD_GO_BINDINGS=OFF",
            "-DBUILD_C_BINDINGS=OFF",
            "-DBUILD_TESTS=OFF",
        ]

        build_args = []

        if sys.platform.startswith("darwin"):
            archs = os.environ.get("ARCHFLAGS", "")
            if archs:
                archs = archs.replace("-arch ", "").strip()
                cmake_args += [f"-DCMAKE_OSX_ARCHITECTURES={archs}"]
        elif sys.platform.startswith("win"):
            cmake_args += [
                "-A", "x64" if sys.maxsize > 2**32 else "Win32",
                "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE",
                "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE={}".format(extdir.replace('\\', '/')),
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={}".format(extdir.replace('\\', '/')),
            ]

        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            build_args += [f"-j{os.cpu_count() or 1}"]

        cfg = "Debug" if self.debug else "Release"
        build_args += ["--config", cfg]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )

        if sys.platform.startswith("win"):
            print(f"Build completed. Listing files in {self.build_temp}:")
            for root, dirs, files in os.walk(self.build_temp):
                for file in files:
                    if file.endswith(('.pyd', '.dll', '.lib')):
                        print(f"  Found: {os.path.join(root, file)}")


        if sys.platform.startswith("win"):
            search_paths = [
                Path(self.build_temp),
                Path(self.build_temp) / "Release",
                Path(self.build_temp) / "Debug",
            ]

            built_file = None
            for search_path in search_paths:
                if search_path.exists():
                    built_files = list(search_path.rglob("*_aiofiles_core*.pyd"))
                    if built_files:
                        built_file = built_files[0]
                        break

            if built_file and built_file.exists():
                target_file = Path(extdir) / built_file.name
                print(f"Copying {built_file} to {target_file}")
                if not target_file.exists():
                    shutil.copy2(built_file, target_file)
                else:
                    print(f"Target {target_file} already exists")
            else:
                print(f"Warning: Could not find built extension in {search_paths}")
                for search_path in search_paths:
                    if search_path.exists():
                        print(f"Files in {search_path}:")
                        for f in search_path.rglob("*"):
                            print(f"  {f}")


setup(
    ext_modules=[CMakeExtension("_aiofiles_core")],
    cmdclass={"build_ext": CMakeBuild},
    package_dir={"": "src/python"},
    packages=find_packages(where="src/python"),
)
