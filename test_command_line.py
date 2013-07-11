import unittest
import argparse
import pexpect
import sys

class TestInputAPI(unittest.TestCase) :
    def test_simple(self) :
        child = pexpect.spawn('python dedupe_csv.py foo bar')
        child.expect('error: Could not find the file foo')



    
