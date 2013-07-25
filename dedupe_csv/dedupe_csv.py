#! /usr/bin/env python

import argparse
import os
import json
import logging

import csvhelpers
import dedupe
import labeler

import itertools

parser = argparse.ArgumentParser(
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# optional arguments
parser.add_argument('--config_file', type=str,
                    help='Path to configuration file. Must provide either a config_file or input_file and filed_names.')

parser.add_argument('--input_files', type=str, nargs="+",
                    help='List of CSV files to deduplicate')
parser.add_argument('--field_names', type=str, nargs="+",
                    help='List of column names for dedupe to pay attention to')
parser.add_argument('--output_file', type=str,
                    help='CSV file to store deduplication results')
parser.add_argument('--skip_training', action='store_true',
                    help='Skip labeling examples by user and read training from training_file only')
parser.add_argument('--training_file', type=str, default='training.json',
                    help='Path to a new or existing file consisting of labeled training examples')
parser.add_argument('--sample_size', type=int, default=150000,
                    help='Number of random sample pairs to train off of')
parser.add_argument('--recall_weight', type=int, default=2,
                    help='Threshold that will maximize a weighted average of our precision and recall')
parser.add_argument('-v', '--verbose', action='count', default=0)

class DedupeCSV :

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
    if 'input_files' in args_d :
      args_d['arg_input_files'] = args_d['input_files']
      del args_d['input_files']
      

    configuration.update(args_d)

    print configuration

    if ('arg_input_files' in configuration 
        and 'input_files' in configuration) :
      raise parser.error("input_files cannot be set in both the config file and the command line")

    if ('arg_input_files' in configuration
        and 'field_names' in configuration) :

      configuration['input_files'] = [{"file_name" : input_file, 
                                       "fields_names" : configuration["field_names"]}
                                      for input_file
                                      in configuration['arg_input_files']]

    # set defaults
    try :
      self.input_files = configuration['input_files']
      print configuration['input_files']
    except KeyError :
      raise parser.error("You must provide an input_file")

    try : 
      self.field_names = configuration['field_names']
    except KeyError :
      raise parser.error("You must provide field_names")

    self.output_file = configuration.get('output_file', None)
    self.skip_training = configuration.get('skip_training', False)
    self.training_file = configuration.get('training_file', None)
    self.sample_size = configuration.get('sample_size', 150000)
    self.recall_weight = configuration.get('recall_weight', 2)

    if 'field_definition' in configuration :
      self.field_definition = configuration['field_definition']
    else :
      self.field_definition = dict((field, {'type' : 'String'}) 
                                   for field in self.field_names)
      

  def main(self) :

    data = []
    for input_file in self.input_files:

      # import the specified CSV file
      logging.info('reading  %s ...', input_file['file_name'])

      try:
        data.extend(csvhelpers.readData(input_file, self.field_names))
      except IOError:
        raise parser.error("Could not find the file " + input_file['file_name'] + '. Did you name it correctly?')

    data_d = dict(zip(itertools.count(), data))
    logging.debug(data_d[0])
    logging.info('imported %d rows', len(data_d))

    # sanity check for provided field names in CSV file
    for field in self.field_definition :
      if not field in data_d[0]:
        raise parser.error("Could not find field '" + field + "' in input_file")

    # Set up our data sample
    logging.info('taking a sample of %d possible pairs', self.sample_size)
    data_sample = dedupe.dataSample(data_d, self.sample_size)

    logging.info('using fields:', self.field_definition.keys())
    # # Create a new deduper object and pass our data model to it.
    deduper = dedupe.Dedupe(self.field_definition)

    # If we have training data saved from a previous run of dedupe,
    # look for it an load it in.
    # __Note:__ if you want to train from scratch, delete the training_file

    if os.path.exists(self.training_file):
      logging.info('reading labeled examples from ', self.training_file)
      deduper.train(data_sample, self.training_file)
    elif self.skip_training:
      raise parser.error("You need to provide an existing training_file or run this script without --skip_training")

  if not SKIP_TRAINING:
    print 'starting active labeling...'
    deduper.train(data_sample, labeler.label)

      # When finished, save our training away to disk
      logging.info('saving training data to', self.training_file)
      deduper.writeTraining(self.training_file)
    else:
      logging.info('skipping the training step')

    # ## Blocking

    logging.info('blocking...')
    # Initialize our blocker. We'll learn our blocking rules if we haven't
    # loaded them from a saved settings file.
    blocker = deduper.blockingFunction()

    # Load all the original data in to memory and place
    # them in to blocks. Each record can be blocked in many ways, so for
    # larger data, memory will be a limiting factor.

    blocked_data = dedupe.blockData(data_d, blocker)

    # ## Clustering

    # Find the threshold that will maximize a weighted average of our precision and recall. 
    # When we set the recall weight to 2, we are saying we care twice as much
    # about recall as we do precision.
    #
    # If we had more data, we would not pass in all the blocked data into
    # this function but a representative sample.

    logging.info('finding a good threshold with a recall_weight of', 
                 self.recall_weight)
    threshold = deduper.goodThreshold(blocked_data, recall_weight=self.recall_weight)

    # `duplicateClusters` will return sets of record IDs that dedupe
    # believes are all referring to the same entity.

    logging.info('clustering...')
    clustered_dupes = deduper.duplicateClusters(blocked_data, threshold)

    logging.info('# duplicate sets', len(clustered_dupes))

    # write out our results
    if self.output_file == None:
      self.output_file = self.input_files[0]['file_name'].replace('.','_cleaned.')

    csvhelpers.writeResults(clustered_dupes, self.input_files[0]['file_name'], self.output_file)

def launch_new_instance():
    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose == 1:
      log_level = logging.INFO
    elif args.verbose >= 2:
      log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    d = DedupeCSV(args)
    d.main()
    
if __name__ == "__main__":
    launch_new_instance()
