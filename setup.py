from setuptools import setup

setup(
    name = "csvdedupe",
    version = '0.1.1',
    description="Command line tools for deduplicating and merging csv files",
    long_description=open('README.md').read(),
    author="Forest Gregg, Derek Eder",
    license="MIT",
    packages=['csvdedupe'],
    entry_points ={
        'console_scripts': [
            'csvdedupe = csvdedupe.csvdedupe:launch_new_instance',
            'csvlink = csvdedupe.csvlink:launch_new_instance'
        ]
    },
    install_requires = [
        'argparse>=1.2.1',
        'dedupe']
)
