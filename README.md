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

```console
./dedupe_csv.py --input_file=your_file.csv --field_names="Field1,Field2,Field3"
```

### arguments:
  * `--config_file` Path to configuration file. Must provide either a config_file or input_file and filed_names.
  * `--input_file`            CSV file to deduplicate
  * `--field_names`           List of column names for dedupe to pay attention to
  * `-h`, `--help`            show this help message and exit
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

### Example

```console
./dedupe_csv.py --input_file=csv_example_messy_input.csv --field_names="Site name,Address,Zip,Phone" --training_file my_training.json --skip_training
```
