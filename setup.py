#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import os
import platform
import re
from os import path

from setuptools import find_packages
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))

__version__ = '0.0.4'


def gh(name, version):
    package = name.split('/')[1]
    if 'GHE_ACCESS_TOKEN' in os.environ:
        proto = 'git+https://{}@'.format(os.environ['GHE_ACCESS_TOKEN'])
    elif 'CDP_BUILD_VERSION' in os.environ:
        proto = 'git+https://'
    else:
        proto = 'git+ssh://git@'
    return '{proto}github.com//{name}.git@{version}' \
           '#egg={package}-{version}'.format(**locals())


py_major_version, py_minor_version, _ = (
    int(re.sub('[^\d]+.*$', '', v)) for v in platform.python_version_tuple())  # dealing with 2.7.2+ and 2.7.15rc1


def load_requirements_file(path):
    content = open(os.path.join(__location__, path)).read().splitlines()
    requires = [req for req in content if req != '' and not req.startswith("#")]
    return requires


p = path.abspath(path.dirname(__file__))
with open(path.join(p, 'README.md')) as f:
    README = f.read()

setup(
    name="python-athena",
    version="0.2.1",
    packages=find_packages(),
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=load_requirements_file('requirements.txt'),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"]
    },
    # metadata for upload to PyPI
    author="kushwahamit2016@gmail.com",
    author_email="kushwahamit2016@gmail.com",
    description="Athena client to do query on Amazon Athena",
    url="https://github.com/yardstick17/PyAthena",
    project_urls={
        "Bug Tracker": "https://github.com/yardstick17/PyAthena",
        "Documentation": "https://github.com/yardstick17/PyAthena",
        "Source Code": "https://github.com/yardstick17/PyAthena",
    },
)
