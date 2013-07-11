# Dedupe CSV

Command line tool for deduplicating CSV files.

## Installation

```console
git clone git@github.com:datamade/dedupe-csv.git
cd dedupe-csv
pip install -r requirements.txt
```

## Usage

```console
python dedupe_csv.py input_file output_file field_names
```

### positional arguments
* `input_file` CSV file to deduplicate
* `output_file` CSV file to store deduplication results
* `field_names` List of column names for dedupe to pay attention to

### optional arguments
* `-h`, `--help` show this help message and exit

### Example

```console
python dedupe_csv.py csv_example_messy_input.csv output.csv "Site name,Address,Zip,Phone"
```