import re
from pathlib import Path
import platform

from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize


PLATFORM = platform.system().lower()
ROOT_DIR = Path(__file__).parent
PACKAGE_DIR = ROOT_DIR / 'shufflish'


def ext_modules():
    include_dirs = [str(PACKAGE_DIR)]
    cython_files = [PACKAGE_DIR / '_affine.pyx']
    for cython_file in cython_files:
        if cython_file.exists():
            cythonize(str(cython_file))

    # source files must be strings relative to setup.py
    sources = ['shufflish/_affine.c']

    extra_link_args = []
    extra_compile_args = []
    if PLATFORM == 'linux':
        extra_link_args.extend([
            '-Wl,'  # following are linker options
            '--strip-all,'  # Remove all symbols
            '--exclude-libs,ALL,'  # Do not export symbols
            '--gc-sections',  # Remove unused sections
        ])
        extra_compile_args.extend([
            '-O3',  # gotta go fast
            '-ffunction-sections', # for --gc-sections
            '-fdata-sections', # for --gc-sections
        ])

    return [Extension(
        'shufflish._affine',
        sources,
        language='C',
        include_dirs=include_dirs,
        extra_link_args=extra_link_args,
        extra_compile_args=extra_compile_args,
    )]


def exclude_package_data():
    packages = find_packages(
        include=['shufflish', 'shufflish.*'],
    )
    patterns = ('*.h', '*.c', '*.pyx', '*.pxd')
    return {
        package: patterns
        for package in packages
    }


setup(
    ext_modules=ext_modules(),
    exclude_package_data=exclude_package_data()
)
