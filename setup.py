from setuptools import setup
import sys

requirements = ['future>=0.14',
                'dedupe>=1.6']

if sys.version < '3':
    requirements += ['backports.csv']

setup(
    name = "csvdedupe",
    version = '0.1.15',
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
