# Copyright 2025 Daniil Shmelev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

from pathlib import Path
import shutil
import os
import sys
import platform

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

ALLOW_EDITABLE = False
if 'ALLOW_EDITABLE' in os.environ and int(os.environ['ALLOW_EDITABLE']) == 1:
    ALLOW_EDITABLE = True

# Editable installs don't compile the dlls. Block them entirely.
if any(arg in ["develop", "editable", "-e"] for arg in sys.argv) and not ALLOW_EDITABLE:
    raise RuntimeError("This package cannot be installed in editable mode.")

REBUILD = True
USE_CUDA = 'CUDA_PATH' in os.environ
if 'CUSIG' in os.environ and int(os.environ['CUSIG']) == 0:
    USE_CUDA = False

USE_AVX = True
if 'SIGLIB_VEC' in os.environ and int(os.environ['SIGLIB_VEC']) == 0:
    USE_AVX = False

# Only support Windows, Linux and MacOS
SYSTEM = platform.system()
if SYSTEM not in ['Windows', 'Linux', 'Darwin']:
    raise RuntimeError("Error while installing pySigLib: unsupported system '" + SYSTEM + "'")

# Don't support CUDA on MacOS
if SYSTEM == 'Darwin':
    USE_CUDA = False

# Get lib extension
if SYSTEM == 'Windows':
    LIB_PREFIX = ''
elif SYSTEM == 'Linux':
    LIB_PREFIX = 'lib'
else:
    LIB_PREFIX = 'lib'

if SYSTEM == 'Windows':
    LIB_EXT = '.dll'
elif SYSTEM == 'Linux':
    LIB_EXT = '.so'
else:
    LIB_EXT = '.dylib'

# Get lib names
LIBS = [LIB_PREFIX + 'cpsig' + LIB_EXT]
if USE_CUDA:
    LIBS += [LIB_PREFIX + 'cusig' + LIB_EXT]

class CustomBuild(_build_py):
    def run(self):
        # These imports are delayed until here because they require the packages in 'setup_requires'
        from build_utils import get_b2, build_cpsig, build_cusig, get_avx_info, make_jamfiles

        global REBUILD, SYSTEM, USE_CUDA, USE_AVX, LIBS

        if REBUILD:
            old_build_paths = []
            old_build_paths.append( Path(__file__).parent / 'siglib' / 'x64' )
            old_build_paths.append(Path(__file__).parent / 'siglib' / 'bin')
            old_build_paths.append(Path(__file__).parent / 'siglib' / 'cpsig'/ 'x64')
            old_build_paths.append(Path(__file__).parent / 'siglib' / 'cpsig' / 'bin')
            old_build_paths.append(Path(__file__).parent / 'siglib' / 'cusig' / 'x64')
            old_build_paths.append(Path(__file__).parent / 'siglib' / 'cusig' / 'bin')

            for path_ in old_build_paths:
                if os.path.exists(path_):
                    shutil.rmtree(path_)

            # Create log file
            parent_dir = Path(__file__).parent
            log_path = parent_dir / 'pysiglib' / '_build_log.txt'

            if os.path.exists(log_path):
                os.remove(log_path)

            with open(log_path, "w") as log_file:

                if USE_CUDA:
                    print("Found CUDA_PATH, attempting to build with CUDA. To build without CUDA, run 'CUSIG=0 pip install pysiglib' instead.")
                    log_file.write("Found CUDA_PATH, attempting to build with CUDA. To build without CUDA, run 'CUSIG=0 pip install pysiglib' instead.")
                else:
                    print("Building without CUDA.")
                    log_file.write("Building without CUDA.")

                print("Building sigLib, output being written to _build_log.txt")
                get_b2(SYSTEM, log_file)
                instructions = get_avx_info(SYSTEM, log_file)

                if not USE_AVX:
                    instructions = []
                elif 'avx2' not in instructions:
                    USE_AVX = False

                make_jamfiles(SYSTEM, instructions, log_file)
                build_cpsig(SYSTEM, log_file)
                if USE_CUDA:
                    build_cusig(SYSTEM, log_file)

            parent_dir = Path(__file__).parent
            dir_ = parent_dir / 'pysiglib'

            for file in LIBS:
                path = parent_dir / 'siglib' / 'x64' / 'Release' / file
                shutil.copy(path, dir_)

            # Create config file with flags
            parent_dir = Path(__file__).parent
            dir_ = parent_dir / 'pysiglib'
            config_path = dir_ / '_config.py'

            if os.path.exists(config_path):
                os.remove(config_path)

            with open(config_path, 'w') as f:
                f.write("# This file is automatically generated by setup.py and should not be edited.\n")
                f.write("# It contains information about how the package was built.\n")
                f.write(f"SYSTEM = {repr(SYSTEM)}\n")
                f.write(f"BUILT_WITH_CUDA = {USE_CUDA}\n")
                f.write(f"BUILT_WITH_AVX = {USE_AVX}\n")

        super().run()

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='pysiglib',
    version="0.2.2",
    description="Fast Signature Computations on CPU and GPU",
    packages=['pysiglib'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Win32 (MS Windows)",
            "Intended Audience :: Developers",
            "Intended Audience :: Financial and Insurance Industry",
            "Intended Audience :: Healthcare Industry",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Natural Language :: English",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: Unix",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python",
            "Programming Language :: C++",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Mathematics",
        ],
    url="https://github.com/daniil-shmelev/pySigLib",
    author="Daniil Shmelev",
    author_email="daniil.shmelev23@imperial.ac.uk",
    setup_requires = [
        "Requests",
        "setuptools"
    ],
    install_requires=[
        "numpy",
        "torch"
        ],
    include_package_data=True,
    package_data={'': LIBS + ['_config.py', '_build_log.txt']},
    cmdclass={
        'build_py': CustomBuild,
    },
)

#################################################
## Note on installing and/or uploading to PyPi
#################################################
#
# pySigLib needs to compile the C++ dlls during install. This step is skipped during editable installs,
# or installs from bdist/wheels. Editable installs are automatically blocked by this setup.py, although
# this behaviour can be overwritten by setting the environment variable ALLOW_EDITABLE=1 in exceptional
# cases where the editable install is required and you've precompiled the dlls separately.
#
# To distribute the package properly, use an sdist. For PyPi:
#
# python -m setup.py sdist
# twine check dist/*
# twine upload -r testpypi dist/*
#
