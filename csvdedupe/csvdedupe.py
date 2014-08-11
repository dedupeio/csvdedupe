#! /usr/bin/env python

import argparse
import os
import sys
import json
import logging
from cStringIO import StringIO
import shutil

import csvhelpers
import dedupe

import itertools

parser = argparse.ArgumentParser(
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# positional arguments
parser.add_argument('input', nargs='?', default=sys.stdin,
                    help='The CSV file to operate on. If omitted, will accept input on STDIN.')

# optional arguments
parser.add_argument('--config_file', type=str,
                    help='Path to configuration file. Must provide either a config_file or input and filed_names.')
parser.add_argument('--field_names', type=str, nargs="+",
                    help='List of column names for dedupe to pay attention to')
parser.add_argument('--output_file', type=str,
                    help='CSV file to store deduplication results')
parser.add_argument('--skip_training', action='store_true',
                    help='Skip labeling examples by user and read training from training_file only')
parser.add_argument('--training_file', type=str, 
                    help='Path to a new or existing file consisting of labeled training examples')
parser.add_argument('--sample_size', type=int, 
                    help='Number of random sample pairs to train off of')
parser.add_argument('--recall_weight', type=int, 
                    help='Threshold that will maximize a weighted average of our precision and recall')
parser.add_argument('--destructive', action='store_true',
                    help='Output file will contain unique records only')
parser.add_argument('-v', '--verbose', action='count', default=0)

class CSVDedupe :

  def __init__(self, args) :
    configuration = {}

    if args.config_file:
      #read from configuration file
      try:
        with open(args.config_file, 'r') as f:
          config = json.load(f)
          configuration.update(config)
      except IOError:
        raise parser.error("Could not find config file " + args.config_file + '. Did you name it correctly?')

    # override if provided from the command line
    args_d = vars(args)
    args_d = dict((k,v) for (k,v) in args_d.items() if v is not None)
    configuration.update(args_d)

    # set defaults
    try :
      # take in STDIN input or open the file
      if isinstance(configuration['input'], file):
        if not sys.stdin.isatty() :
          self.input = configuration['input'].read()
          # We need to get control of STDIN again.
          # This is a UNIX/Mac OSX solution only
          # http://stackoverflow.com/questions/7141331/pipe-input-to-python-program-and-later-get-input-from-user
          # 
          # Same question has a Windows solution
          sys.stdin = open('/dev/tty') # Unix only solution, 
        else :
          raise parser.error("No input file or STDIN specified.")
      else:
        try :
          self.input = open(configuration['input'], 'rU').read()
        except IOError :
          raise parser.error("Could not find the file %s" % (configuration['input'],))
    except KeyError :
          raise parser.error("No input file or STDIN specified.")

    try : 
      self.field_names = configuration['field_names']
    except KeyError :
      raise parser.error("You must provide field_names")

    self.output_file = configuration.get('output_file', None)
    self.skip_training = configuration.get('skip_training', False)
    self.training_file = configuration.get('training_file', 'training.json')
    self.sample_size = configuration.get('sample_size', 150000)
    self.recall_weight = configuration.get('recall_weight', 2)
    self.destructive = configuration.get('destructive', False)
    
    if 'field_definition' in configuration :
      self.field_definition = configuration['field_definition']
    else :
      self.field_definition = [{'field' : field, 'type' : 'String'} 
                               for field in self.field_names]
      

  def main(self) :

    data_d = {}
    # import the specified CSV file

    data_d = csvhelpers.readData(self.input, self.field_names)
    
    logging.info('imported %d rows', len(data_d))

    # sanity check for provided field names in CSV file
    for field in self.field_definition :
      if field['type'] != 'Interaction' :
        if not field['field'] in data_d[0]:
        
          raise parser.error("Could not find field '" + field['field'] + "' in input")

    logging.info('using fields: %s' % [field['field'] for 
                                       field in self.field_definition])
    # # Create a new deduper object and pass our data model to it.
    deduper = dedupe.Dedupe(self.field_definition)

    # Set up our data sample
    logging.info('taking a sample of %d possible pairs', self.sample_size)
    deduper.sample(data_d, self.sample_size)

    # If we have training data saved from a previous run of dedupe,
    # look for it an load it in.
    # __Note:__ if you want to train from scratch, delete the training_file

    if os.path.exists(self.training_file):
      logging.info('reading labeled examples from %s' % self.training_file)
      with open(self.training_file) as tf :
        deduper.readTraining(tf)
    elif self.skip_training:
      raise parser.error("You need to provide an existing training_file or run this script without --skip_training")

    if not self.skip_training:
      logging.info('starting active labeling...')

      dedupe.consoleLabel(deduper)

      # When finished, save our training away to disk
      logging.info('saving training data to %s' % self.training_file)
      with open(self.training_file, 'w') as tf :
        deduper.writeTraining(tf)
    else:
      logging.info('skipping the training step')
      
    deduper.train()

    # ## Blocking

    logging.info('blocking...')

    # ## Clustering

    # Find the threshold that will maximize a weighted average of our precision and recall. 
    # When we set the recall weight to 2, we are saying we care twice as much
    # about recall as we do precision.
    #
    # If we had more data, we would not pass in all the blocked data into
    # this function but a representative sample.

    logging.info('finding a good threshold with a recall_weight of %s' % 
                 self.recall_weight)
    threshold = deduper.threshold(data_d, recall_weight=self.recall_weight)

    # `duplicateClusters` will return sets of record IDs that dedupe
    # believes are all referring to the same entity.

    logging.info('clustering...')
    clustered_dupes = deduper.match(data_d, threshold)

    logging.info('# duplicate sets %s' % len(clustered_dupes))

    write_function = csvhelpers.writeResults
    # write out our results
    if self.destructive:
      write_function = csvhelpers.writeUniqueResults

    if self.output_file :
      with open(self.output_file, 'w') as output_file :
        write_function(clustered_dupes, self.input, output_file)
    else :
        write_function(clustered_dupes, self.input, sys.stdout)


def launch_new_instance():
    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose == 1:
      log_level = logging.INFO
    elif args.verbose >= 2:
      log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    d = CSVDedupe(args)
    d.main()
    
if __name__ == "__main__":
    launch_new_instance()
