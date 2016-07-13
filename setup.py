from setuptools import setup
import sys

requirements = ['future',
                'dedupe>=1.2.3']

if sys.version < '3':
    requirements += ['backports.csv']

setup(
    name = "csvdedupe",
    version = '0.1.14',
    description="Command line tools for deduplicating and merging csv files",
    author="Forest Gregg, Derek Eder",
    license="MIT",
    packages=['csvdedupe'],
    entry_points ={
        'console_scripts': [
            'csvdedupe = csvdedupe.csvdedupe:launch_new_instance',
            'csvlink = csvdedupe.csvlink:launch_new_instance'
        ]
    },
    install_requires = requirements
)
