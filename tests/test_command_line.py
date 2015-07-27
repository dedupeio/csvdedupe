import unittest
import argparse
import pexpect
import sys

class TestCSVDedupe(unittest.TestCase) :

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

class TestCSVLink(unittest.TestCase) :

    def test_no_parameters(self):
      child = pexpect.spawn('csvlink')
      if sys.version < '3' :
          child.expect('error: too few arguments')
      else :
          child.expect('error: the following arguments are required: input')

    def test_one_argument(self):
      child = pexpect.spawn('csvlink examples/restaurant-1.csv')
      child.expect('error: You must provide two input files.')

    def test_input_file_1_and_field_names(self) :
      child = pexpect.spawn('csvlink foo1 examples/restaurant-1.csv --field_names foo')
      child.expect('error: Could not find the file foo1')

    def test_input_file_2_and_field_names(self) :
      child = pexpect.spawn('csvlink examples/restaurant-1.csv foo2 --field_names foo')
      child.expect('error: Could not find the file foo2')

    def test_incorrect_fields(self) :
      child = pexpect.spawn('csvlink examples/restaurant-1.csv examples/restaurant-2.csv --field_names_1 name address city foo --field_names_2 name address city cuisine' )
      child.expect("error: Could not find field 'foo'")
