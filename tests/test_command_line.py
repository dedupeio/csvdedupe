import unittest
import argparse
import pexpect
import sys

class TestInputAPI(unittest.TestCase) :

    def test_no_parameters(self):
      child = pexpect.spawn('dedupe')
      child.expect('error: You must provide an input_file and filed_names.')

    def test_input_file_and_field_names(self) :
      child = pexpect.spawn('dedupe --input_file=foo --field_names=bar')
      child.expect('error: Could not find the file foo')

    def test_config_file(self) :
      child = pexpect.spawn('dedupe --config_file=foo.json')
      child.expect('error: Could not find config file foo.json')

    def test_incorrect_fields(self) :
      child = pexpect.spawn('dedupe --input_file=examples/csv_example_messy_input.csv --field_names="Site name,Address,Zip,foo"')
      child.expect("error: Could not find field 'foo'")