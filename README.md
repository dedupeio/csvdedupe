# Dedupe CSV

Command line tool for deduplicating CSV files.

[![Build Status](https://travis-ci.org/datamade/dedupe-csv.png?branch=master)](https://travis-ci.org/datamade/dedupe-csv)

## Installation

```console
git clone git@github.com:datamade/dedupe-csv.git
cd dedupe-csv
pip install -r requirements.txt
python setup.py install
```

## Usage

Provide an input file and field names
```console
dedupe --input_file=csv_example_messy_input.csv --field_names="Site name,Address,Zip,Phone"
```

__or__

Define everything in a config file
```console
dedupe --config_file=config.json
```

### Example config file

```json
{
  "input_files": [
    {
      "file_name": "examples/multi_file_part_1.csv",
      "fields_names": "Site name,Address,Zip,Phone"
    }
  ],
  "field_names": "Site name,Address,Zip,Phone",
  "output_file": "examples/output.csv",
  "skip_training": false,
  "training_file": "training.json",
  "sample_size": 150000,
  "recall_weight": 2
}
```

### Arguments:

#### Required

Either
  * `--config_file` Path to configuration file.

Or
  * `--input_file`            CSV file to deduplicate
  * `--field_names`           List of column names for dedupe to pay attention to

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