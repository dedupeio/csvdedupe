# Dedupe CSV

Command line tool for deduplicating CSV files.

[![Build Status](https://travis-ci.org/datamade/csvdedupe.png?branch=master)](https://travis-ci.org/datamade/csvdedupe)

## Installation

```console
git clone git@github.com:datamade/csvdedupe.git
cd csvdedupe
pip install "numpy>=1.6"
pip install -r requirements.txt
python setup.py install
```

## Usage

Provide an input file and field names
```console
csvdedupe examples/multi_file_part_1.csv --field_names "Site name" Address Zip Phone --output_file output.txt
```

__or__

Pipe it, UNIX style
```console
cat examples/multi_file_part_1.csv | csvdedupe --field_names "Site name" Address Zip Phone > output.txt
```

__or__

Define everything in a config file
```console
csvdedupe examples/multi_file_part_1.csv --config_file=config.json
```

### Example config file

```json
{
  "field_names": ["Site name", "Address", "Zip", "Phone"],
  "field_definition" : {"Site name" : {"type" : "String"},
                        "Address"   : {"type" : "String"},
                        "Zip"       : {"type" : "String",
                                       "Has Missing" : true},
                        "Phone"     : {"type" : "String",
                                       "Has Missing" : true}},

  "output_file": "examples/output.csv",
  "skip_training": false,
  "training_file": "training.json",
  "sample_size": 150000,
  "recall_weight": 2
}
```

### Arguments:

#### Required

  * `input files`  CSV file to deduplicate or a CSV file piped into dedupe 

Either
  * `--config_file` Path to configuration file.
  * `--field_names` List of column names for dedupe to pay attention to

#### Optional
  * `--output_file OUTPUT_FILE`
                        CSV file to store deduplication results (default:
                        None)
  * `--skip_training`       Skip labeling examples by user and read training from
                        training_file only (default: False)
  * `--training_file TRAINING_FILE`
                        Path to a new or existing file consisting of labeled
                        training examples (default: training.json)
  * `--sample_size SAMPLE_SIZE`
                        Number of random sample pairs to train off of
                        (default: 150000)
  * `--recall_weight RECALL_WEIGHT`
                        Threshold that will maximize a weighted average of our
                        precision and recall (default: 2)
  * `-h`, `--help`            show help message and exit
