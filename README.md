# Dedupe CSV

Command line tool for using the [dedupe python library](https://github.com/open-city/dedupe/) for deduplicating CSV files.

[![Build Status](https://travis-ci.org/datamade/csvdedupe.png?branch=master)](https://travis-ci.org/datamade/csvdedupe)

## Installation and dependencies

csvdedupe requires [numpy](http://numpy.scipy.org/), which can be complicated to install. 
If you are installing numpy for the first time, 
[follow these instructions](http://docs.scipy.org/doc/numpy/user/install.html). You'll need to version 1.6 of numpy or higher.

After numpy is set up, then install the following:
* [fastcluster](http://math.stanford.edu/~muellner/fastcluster.html)
* [hcluster](http://code.google.com/p/scipy-cluster/)
* [networkx](http://networkx.github.com/)

```bash
git clone git@github.com:datamade/csvdedupe.git
cd csvdedupe
pip install "numpy>=1.6"
pip install -r requirements.txt
python setup.py install
```

## Usage

Provide an input file and field names
```bash
csvdedupe examples/csv_example_messy_input.csv --field_names "Site name" Address Zip Phone --output_file output.txt
```

__or__

Pipe it, UNIX style
```bash
cat examples/csv_example_messy_input.csv | csvdedupe --skip_training --field_names "Site name" Address Zip Phone > output.txt
```

__or__

Define everything in a config file
```bash
csvdedupe examples/csv_example_messy_input.csv --config_file=config.json
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

  * `input` a CSV file name or piped CSV file to deduplicate

Either
  * `--config_file` Path to configuration file.

Or
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
 
## Training

The _secret sauce_ of csvdedupe is human input. In order to figure out the best rules to deduplicate a set of data, you must give it a set of labeled examples to learn from. 

The more labeled examples you give it, the better the deduplication results will be. At minimum, you should try to provide __10 positive matches__ and __10 negative matches__.

Here's an example labeling operation:

```bash
Phone :  2850617
Address :  3801 s. wabash
Zip :
Site name :  ada s. mckinley st. thomas cdc

Phone :  2850617
Address :  3801 s wabash ave
Zip :
Site name :  ada s. mckinley community services - mckinley - st. thomas

Do these records refer to the same thing?
(y)es / (n)o / (u)nsure / (f)inished
```

### Preprocessing
csvdedupe attempts to convert all strings to ASCII, ignores case, new lines, and padding whitespace. This is all
probably uncontroversial except the conversion to ASCII. Basically, we had to choose between two ways of handling
extended characters.

```
distance("Tomas", "Tomás')  = distance("Tomas", "Tomas")
```

__or__

```
distance("Tomas, "Tomás") = distance("Tomas", "Tomzs")
```

We chose the first option. While it is possible to do something more sophisticated, this option seems to work pretty
for Latin alphabet languages.

or

distance("Thomas, "Thomás") = distance("Thomas", "Thomzs")









