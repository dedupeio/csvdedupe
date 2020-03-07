from setuptools import setup
import sys

requirements = ['future>=0.14',
                'dedupe>=1.6,<2']

if sys.version < '3':
    requirements += ['backports.csv']


from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "csvdedupe",
    version = '0.1.20',
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
    install_requires = requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
