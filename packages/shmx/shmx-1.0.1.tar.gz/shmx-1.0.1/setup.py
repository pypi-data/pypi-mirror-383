"""SHMX: High-performance shared-memory IPC for frame streaming
Setup script for building Python extension
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import sysconfig

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CustomSdist(sdist):
    """Custom sdist to ensure headers are copied before packaging"""
    def run(self):
        # Copy headers from parent directory to local src directory
        src_parent = os.path.join(os.path.dirname(__file__), "..", "src")
        src_local = os.path.join(os.path.dirname(__file__), "src")

        if os.path.exists(src_parent):
            os.makedirs(src_local, exist_ok=True)
            for header in Path(src_parent).glob("*.h"):
                print(f"Copying {header.name} to {src_local}")
                shutil.copy2(header, src_local)

        # Run the original sdist command
        sdist.run(self)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        # Copy headers from parent directory if they exist and we're in development
        src_parent = os.path.join(ext.sourcedir, "..", "src")
        src_local = os.path.join(ext.sourcedir, "src")

        # Try to copy headers if they're in parent directory but not in local
        if os.path.exists(src_parent) and not os.path.exists(src_local):
            # Development build - copy headers
            print(f"Development build: copying headers from {src_parent} to {src_local}")
            os.makedirs(src_local, exist_ok=True)
            for header in Path(src_parent).glob("*.h"):
                shutil.copy2(header, src_local)

        # Verify headers exist - should be there either from sdist or copied above
        if not os.path.exists(src_local):
            # Print debug info
            print(f"ERROR: Headers directory not found at: {src_local}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Extension source dir: {ext.sourcedir}")
            print(f"Directory contents: {os.listdir(ext.sourcedir)}")
            raise RuntimeError(
                f"Headers directory not found: {src_local}\n"
                f"This usually means the build is not from a proper source distribution. "
                f"Expected headers to be in 'src/' subdirectory."
            )

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DPython_EXECUTABLE={sys.executable}",
            f"-DPython_INCLUDE_DIR={sysconfig.get_path('include')}",
            f"-DPython_LIBRARIES={sysconfig.get_config_var('LIBDIR')}",
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        if platform.system() == "Windows":
            cmake_args += [f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            cmake_args += [f"-DCMAKE_BUILD_TYPE={cfg}"]
            build_args += ["--", "-j4"]

        env = os.environ.copy()
        env["CXXFLAGS"] = f'{env.get("CXXFLAGS", "")} -DVERSION_INFO=\"{self.distribution.get_version()}\"'
        
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=self.build_temp)


setup(
    ext_modules=[CMakeExtension("shmx.shmx_core", sourcedir=".")],
    cmdclass={"build_ext": CMakeBuild, "sdist": CustomSdist},
    zip_safe=False,
)
