import argparse

import csvhelpers
import dedupe

parser = argparse.ArgumentParser()

parser.add_argument('input_file', type=str, 
                    help='CSV file to deduplicate')
parser.add_argument('field_names', type=str,
                    help='List of column names for dedupe to pay attention to')

args = parser.parse_args()

# import the specified CSV file
print 'Reading', args.input_file, '...'
data_d = csvhelpers.readData(args.input_file)
print 'Imported', len(data_d), 'rows'

# Set up our data sample and fields to pass to dedupe
data_sample = dedupe.dataSample(data_d, 150000)

fields = {}
for field in args.field_names.split(','):
  fields[field] = {'type': 'String'}

print 'Using fields:', fields

# # Create a new deduper object and pass our data model to it.
deduper = dedupe.Dedupe(fields)

print 'starting active labeling...'
deduper.train(data_sample, dedupe.training.consoleLabel)

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

threshold = deduper.goodThreshold(blocked_data, recall_weight=2)

# `duplicateClusters` will return sets of record IDs that dedupe
# believes are all referring to the same entity.

print 'clustering...'
clustered_dupes = deduper.duplicateClusters(blocked_data, threshold)

print '# duplicate sets', len(clustered_dupes)

csvhelpers.writeResults(clustered_dupes, args.input_file)