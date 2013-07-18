from setuptools import setup

setup(
    name = "dedupe-csv",
    version = '0.0.1',
    description="Command line tools for deduplicating and merging csv files",
    long_description=open('README.md').read(),
    author="Forest Gregg, Derek Eder",
    license="MIT",
    packages=['dedupe_csv'],
    entry_points ={
        'console_scripts': [
            'dedupe = dedupe_csv.dedupe_csv:launch_new_instance',
        ]
    },
    install_requires = [
        'argparse>=1.2.1',
        'dedupe']
)
