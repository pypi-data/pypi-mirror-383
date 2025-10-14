# Copyright 2024 The QGIF Authors. All Rights Reserved.
#
# Licensed under the Proprietary License;
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py
import os

from qgif import VERSION

REQUIRED_PACKAGES = [
    'numpy',
    'pillow',
    'tqdm',
    'opencv-python'
]

setup(
    name='qgif',
    version=VERSION,
    description='Convert GIF to QGIF, or decode QGIF.',
    author='Hangzhou Nationalchip Inc.',
    author_email='zhengdi@nationalchip.com',
    license='MIT Licence',

    # PyPI package information.
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],

    keywords='qgif nationalchip',

    # Contained modules and scripts.
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,

    package_data={
        'qgif': ['qgif_C/libqgif.so', 'qgif_C/libqgif.dll']
    },
    scripts=['qgif/qgif'],
    entry_points={
    },
)
