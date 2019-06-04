#! /usr/bin/env python
import future
import os
import codecs
import sys
import locale
import logging
from io import StringIO, open
from . import csvhelpers
import dedupe

import itertools


class CSVDedupe(csvhelpers.CSVCommand) :
    def __init__(self):
        super(CSVDedupe, self).__init__()

        # set defaults
        try:
            # take in STDIN input or open the file
            if hasattr(self.configuration['input'], 'read'):
                if not sys.stdin.isatty():
                    self.input = self.configuration['input'].read()
                    # We need to get control of STDIN again.
                    # This is a UNIX/Mac OSX solution only
                    # http://stackoverflow.com/questions/7141331/pipe-input-to-python-program-and-later-get-input-from-user
                    # 
                    # Same question has a Windows solution
                    sys.stdin = open('/dev/tty')  # Unix only solution,
                else:
                    raise self.parser.error("No input file or STDIN specified.")
            else:
                try:
                    self.input = open(self.configuration['input'], encoding='utf-8').read()
                except IOError:
                    raise self.parser.error("Could not find the file %s" %
                                            (self.configuration['input'], ))
        except KeyError:
            raise self.parser.error("No input file or STDIN specified.")

        if self.field_definition is None :
            try:
                self.field_names = self.configuration['field_names']
                self.field_definition = [{'field': field,
                                          'type': 'String'}
                                         for field in self.field_names]
            except KeyError:
                raise self.parser.error("You must provide field_names")
        else :
            self.field_names = [field_def['field']
                                for field_def in self.field_definition]

        self.destructive = self.configuration.get('destructive', False)

    def add_args(self) :
        # positional arguments
        self.parser.add_argument('input', nargs='?', default=sys.stdin,
            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
        self.parser.add_argument('--destructive', action='store_true',
            help='Output file will contain unique records only')


    def main(self):

        data_d = {}
        # import the specified CSV file

        data_d = csvhelpers.readData(self.input, self.field_names, delimiter=self.delimiter)

        logging.info('imported %d rows', len(data_d))

        # sanity check for provided field names in CSV file
        for field in self.field_definition:
            if field['type'] != 'Interaction':
                if not field['field'] in data_d[0]:

                    raise self.parser.error("Could not find field '" +
                                            field['field'] + "' in input")

        logging.info('using fields: %s' % [field['field']
                                           for field in self.field_definition])

        # If --skip_training has been selected, and we have a settings cache still
        # persisting from the last run, use it in this next run.
        # __Note:__ if you want to add more training data, don't use skip training
        if self.skip_training and os.path.exists(self.settings_file):

            # Load our deduper from the last training session cache.
            logging.info('reading from previous training cache %s'
                                                          % self.settings_file)
            with open(self.settings_file, 'rb') as f:
                deduper = dedupe.StaticDedupe(f)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            unique_d, parents = exact_matches(data_d, fields)
                
        else:
            # # Create a new deduper object and pass our data model to it.
            deduper = dedupe.Dedupe(self.field_definition)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            unique_d, parents = exact_matches(data_d, fields)

            # Set up our data sample
            logging.info('taking a sample of %d possible pairs', self.sample_size)
            deduper.sample(unique_d, self.sample_size)

            # Perform standard training procedures
            self.dedupe_training(deduper)

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
        threshold = deduper.threshold(unique_d, recall_weight=self.recall_weight)

        # `duplicateClusters` will return sets of record IDs that dedupe
        # believes are all referring to the same entity.

        logging.info('clustering...')
        clustered_dupes = deduper.match(unique_d, threshold)

        expanded_clustered_dupes = []
        for cluster, scores in clustered_dupes:
            new_cluster = list(cluster)
            new_scores = list(scores)
            for row_id, score in zip(cluster, scores):
                children = parents.get(row_id, [])
                new_cluster.extend(children)
                new_scores.extend([score] * len(children))
            expanded_clustered_dupes.append((new_cluster, new_scores))

        clustered_dupes = expanded_clustered_dupes

        logging.info('# duplicate sets %s' % len(clustered_dupes))

        write_function = csvhelpers.writeResults
        # write out our results
        if self.destructive:
            write_function = csvhelpers.writeUniqueResults

        if self.output_file:
            with open(self.output_file, 'w', encoding='utf-8') as output_file:
                write_function(clustered_dupes, self.input, output_file)
        else:
            if sys.version < '3' :
                out = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
                write_function(clustered_dupes, self.input, out)
            else :
                write_function(clustered_dupes, self.input, sys.stdout)

def exact_matches(data_d, match_fields):
    unique = {}
    redundant = {}
    for key, record in data_d.items():
        record_hash = hash(tuple(record[f] for f in match_fields))
        if record_hash not in redundant:
            unique[key] = record
            redundant[record_hash] = (key, [])
        else:
            redundant[record_hash][1].append(key)

    return unique, {k : v for k, v in redundant.values()}


def launch_new_instance():
    d = CSVDedupe()
    d.main()


if __name__ == "__main__":
    launch_new_instance()
