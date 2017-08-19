"""Setup module"""

import os
import codecs
from setuptools import setup, find_packages

parent_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(parent_dir, 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='monitoring-scripts',

    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    description='Carpe Noctem Tactical Operations Services monitoring scripts',
    long_description=long_description,

    author='Enrico Ghidoni',
    author_email='enricoghdn@gmail.com',

    license='BSD 3-Clause License',

    classifiers=[],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'requests==2.18.3'
    ],

    extras_require={
        'tests': [
            'coverage>=4.4,<5',
            'pytest>=3.2,<4',
            'pytest-mock>=1.6,<2',
            'pytest-cov>=2.5,<3',
            'codacy-coverage>=1.3,<2'
        ]
    },

    entry_points={
        'console_scripts': [
            'http-monitor=monitoring_scripts.http_monitor:http_entry_point',
        ]
    }
)
