#! /usr/bin/env python

import argparse
import os
import json

import csvhelpers
import dedupe
import labeler

parser = argparse.ArgumentParser(
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# optional arguments
parser.add_argument('--config_file', type=str,
                    help='Path to configuration file. Must provide either a config_file or input_file and filed_names.')

parser.add_argument('--input_file', type=str, 
                    help='CSV file to deduplicate')
parser.add_argument('--field_names', type=str,
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

def main(args):

  # set defaults
  INPUT_FILE = None
  FIELD_NAMES = None
  OUTPUT_FILE = None
  SKIP_TRAINING = False
  TRAINING_FILE = 'training.json'
  SAMPLE_SIZE = 150000
  RECALL_WEIGHT = 2

  if args.config_file:
    #read from configuration file
    try:
      with open(args.config_file, 'r') as f:
        config = json.load(f)

      if config['input_file']: INPUT_FILE = config['input_file']
      if config['field_names']: FIELD_NAMES = config['field_names']
      if config['output_file']: OUTPUT_FILE = config['output_file']
      if config['skip_training']: SKIP_TRAINING = config['skip_training']
      if config['training_file']: TRAINING_FILE = config['training_file']
      if config['sample_size']: SAMPLE_SIZE = config['sample_size']
      if config['recall_weight']: RECALL_WEIGHT = config['recall_weight']

    except IOError:
      raise parser.error("Could not find the file " + args.config_file + '. Did you name it correctly?')

  # override if provided from the command line
  if args.input_file: INPUT_FILE = args.input_file
  if args.field_names: FIELD_NAMES = args.field_names
  if args.output_file: OUTPUT_FILE = args.output_file
  if args.skip_training: SKIP_TRAINING = args.skip_training
  if args.training_file: TRAINING_FILE = args.training_file
  if args.sample_size: SAMPLE_SIZE = args.sample_size
  if args.recall_weight: RECALL_WEIGHT = args.recall_weight

  if not INPUT_FILE or not FIELD_NAMES:
    raise parser.error("You must provide an input_file and filed_names. This can be done by specifying them in the config_file or passing them in as parameters.")

  # import the specified CSV file
  print 'reading', INPUT_FILE, '...'

  try:
    data_d = csvhelpers.readData(INPUT_FILE)
  except IOError:
    raise parser.error("Could not find the file " + INPUT_FILE + '. Did you name it correctly?')

  print 'imported', len(data_d), 'rows'

  fields = {}

  for field in FIELD_NAMES.split(','):
    
    # sanity check for provided field names in CSV file
    if not field in data_d[0]:
      raise parser.error("Could not find field '" + field + "' in input_file")
    fields[field] = {'type': 'String'}

  # Set up our data sample
  print 'taking a sample of', SAMPLE_SIZE, 'possible pairs'
  data_sample = dedupe.dataSample(data_d, SAMPLE_SIZE)

  print 'using fields:', fields
  # # Create a new deduper object and pass our data model to it.
  deduper = dedupe.Dedupe(fields)

  # If we have training data saved from a previous run of dedupe,
  # look for it an load it in.
  # __Note:__ if you want to train from scratch, delete the training_file
  if os.path.exists(TRAINING_FILE):
    print 'reading labeled examples from ', TRAINING_FILE
    deduper.train(data_sample, TRAINING_FILE)
  elif SKIP_TRAINING:
    raise parser.error("You need to provide an existing training_file or run this script without --skip_training")

  if not SKIP_TRAINING:
    print 'starting active labeling...'
    deduper.train(data_sample, labeler.consoleLabel)

    # When finished, save our training away to disk
    print 'saving training data to', TRAINING_FILE
    deduper.writeTraining(TRAINING_FILE)
  else:
    print 'skipping the training step'

  # ## Blocking

  print 'blocking...'
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

  print 'finding a good threshold with a recall_weight of', RECALL_WEIGHT
  threshold = deduper.goodThreshold(blocked_data, recall_weight=RECALL_WEIGHT)

  # `duplicateClusters` will return sets of record IDs that dedupe
  # believes are all referring to the same entity.

  print 'clustering...'
  clustered_dupes = deduper.duplicateClusters(blocked_data, threshold)

  print '# duplicate sets', len(clustered_dupes)

  # write out our results
  if OUTPUT_FILE == None:
    OUTPUT_FILE = INPUT_FILE.replace('.','_cleaned.')

  csvhelpers.writeResults(clustered_dupes, INPUT_FILE, OUTPUT_FILE)

def launch_new_instance():
    args = parser.parse_args()
    main(args)
    
if __name__ == "__main__":
    launch_new_instance()