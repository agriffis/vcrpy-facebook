"""vcrpy-facebook setup module based on
https://github.com/pypa/sampleproject
"""
from __future__ import absolute_import, unicode_literals

from setuptools import setup, find_packages
from codecs import open
import os
import sys

here = os.path.dirname(__file__)
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = ['vcrpy']
if sys.version_info < (2 , 7):
    install_requires.append('ordereddict')

setup(
    name='vcrpy-facebook',
    version='0.1',
    description='Facebook filters for vcr.py',
    long_description=long_description,
    url='https://github.com/agriffis/vcrpy-facebook',
    author='Aron Griffis',
    author_email='aron@arongriffis.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='vcrpy vcr.py facebook testing mock http'.split(),
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
)
