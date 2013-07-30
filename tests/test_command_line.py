import unittest
import argparse
import pexpect
import sys

class TestInputAPI(unittest.TestCase) :

    def test_no_parameters(self):
      child = pexpect.spawn('csvdedupe')
      child.expect('error: No input file or STDIN specified.')

    def test_input_file_and_field_names(self) :
      child = pexpect.spawn('csvdedupe foo --field_names bar')
      child.expect('error: Could not find the file foo')

    def test_config_file(self) :
      child = pexpect.spawn('csvdedupe examples/csv_example_messy_input.csv --config_file foo.json')
      child.expect('error: Could not find config file foo.json')

    def test_incorrect_fields(self) :
      child = pexpect.spawn('csvdedupe examples/csv_example_messy_input.csv --field_names "Site name" Address Zip foo')
      child.expect("error: Could not find field 'foo'")

    def test_no_training(self) :
      child = pexpect.spawn('csvdedupe examples/csv_example_messy_input.csv --field_names "Site name" Address Zip Phone --training_file foo.json --skip_training')
      child.expect("error: You need to provide an existing training_file or run this script without --skip_training")
