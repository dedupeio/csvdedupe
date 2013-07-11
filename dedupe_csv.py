#! /usr/bin/env python

import argparse
import os

import csvhelpers
import dedupe

parser = argparse.ArgumentParser(
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# required arguments
parser.add_argument('input_file', type=str, 
                    help='CSV file to deduplicate')
parser.add_argument('field_names', type=str,
                    help='List of column names for dedupe to pay attention to')

# optional arguments
parser.add_argument('--output_file', type=str, default=None,
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

  # import the specified CSV file
  print 'reading', args.input_file, '...'
  data_d = csvhelpers.readData(args.input_file)
  print 'imported', len(data_d), 'rows'

  # Set up our data sample and fields to pass to dedupe
  print 'taking a sample of', args.sample_size, 'possible pairs'
  data_sample = dedupe.dataSample(data_d, args.sample_size)

  fields = {}
  for field in args.field_names.split(','):
    fields[field] = {'type': 'String'}

  print 'using fields:', fields

  # # Create a new deduper object and pass our data model to it.
  deduper = dedupe.Dedupe(fields)

  # If we have training data saved from a previous run of dedupe,
  # look for it an load it in.
  # __Note:__ if you want to train from scratch, delete the training_file
  if os.path.exists(args.training_file):
    print 'reading labeled examples from ', args.training_file
    deduper.train(data_sample, args.training_file)
  elif args.skip_training:
    raise parser.error("You need to provide an existing training_file or run this script without --skip_training")

  if args.skip_training == False:
    print 'starting active labeling...'
    deduper.train(data_sample, dedupe.training.consoleLabel)

    # When finished, save our training away to disk
    print 'saving training data to', args.training_file
    deduper.writeTraining(args.training_file)
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

  print 'finding a good threshold with a recall_weight of', args.recall_weight
  threshold = deduper.goodThreshold(blocked_data, recall_weight=args.recall_weight)

  # `duplicateClusters` will return sets of record IDs that dedupe
  # believes are all referring to the same entity.

  print 'clustering...'
  clustered_dupes = deduper.duplicateClusters(blocked_data, threshold)

  print '# duplicate sets', len(clustered_dupes)

  # write out our results
  output_file = args.output_file
  if output_file == None:
    output_file = args.input_file.replace('.','_cleaned.')

  csvhelpers.writeResults(clustered_dupes, args.input_file, output_file)

if __name__ == '__main__':
  args = parser.parse_args()
  main(args)