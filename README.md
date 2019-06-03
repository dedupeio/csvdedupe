# csvdedupe

Command line tools for using the [dedupe python library](https://github.com/open-city/dedupe/) for deduplicating CSV files.

Two easy commands:

`csvdedupe` - takes a messy input file or STDIN pipe and identifies duplicates.

`csvlink` - takes two CSV files and finds matches between them.

[Read more about csvdedupe on OpenNews Source](http://source.opennews.org/en-US/articles/introducing-cvsdedupe/)


[![Build Status](https://travis-ci.org/dedupeio/csvdedupe.png?branch=master)](https://travis-ci.org/dedupeio/csvdedupe)

## Installation and dependencies

```
pip install csvdedupe
```

## Getting Started

### csvdedupe

`csvdedupe` takes a messy input file or STDIN pipe and identifies duplicates. To get started, pick one of three deduping strategies: call `csvdedupe` with arguments, pipe your file using UNIX, or define a config file.

Provide an input file, field names, and output file:
```bash
csvdedupe examples/csv_example_messy_input.csv \
          --field_names "Site name" Address Zip Phone \
          --output_file output.csv
```

__or__

Pipe it, UNIX style:
```bash
cat examples/csv_example_messy_input.csv | csvdedupe --skip_training \
          --field_names "Site name" Address Zip Phone > output.csv
```

__or__

Define everything in a config file:
```bash
csvdedupe examples/csv_example_messy_input.csv \
            --config_file=config.json
```

**Your config file may look like this:**

```json
{
  "field_names": ["Site name", "Address", "Zip", "Phone"],
  "field_definition" : [{"field" : "Site name", "type" : "String"},
                        {"field" : "Address", "type" : "String"},
                        {"field" : "Zip", "type" : "String",
                         "Has Missing" : true},
                        {"field" : "Phone", "type" : "String",
                         "Has Missing" : true}],
  "output_file": "examples/output.csv",
  "skip_training": false,
  "training_file": "training.json",
  "sample_size": 150000,
  "recall_weight": 2
}
```

#### To use `csvdedupe` you absolutely need:

  * `input` a CSV file name or piped CSV file to deduplicate

Either
  * `--config_file` Path to configuration file.

Or
  * `--field_names` List of column names for dedupe to pay attention to

#### You may also need:
  * `--output_file OUTPUT_FILE`
                        CSV file to store deduplication results (default:
                        None)
  * `--destructive`         Output file will contain unique records only
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
  * `-d`, `--delimiter`
                        Delimiting character of the input CSV file (default: ,)
  * `-h`, `--help`           show help message and exit


---
### csvlink
`csvlink` takes two CSV files and finds matches between them.

Provide an input file, field names, and output file:
```bash
csvlink examples/restaurant-1.csv examples/restaurant-2.csv \
            --field_names name address city cuisine \
            --output_file output.csv
```

__or__

Line up different field names from each file:
```bash
csvlink examples/restaurant-1.csv examples/restaurant-2.csv \
            --field_names_1 name address city cuisine \
            --field_names_2 restaurant street city type \
            --output_file output.csv
```

__or__

Pipe the output to STDOUT:
```bash
csvlink examples/restaurant-1.csv examples/restaurant-2.csv \
            --field_names name address city cuisine \
            > output.csv
```

__or__

Define everything in a config file:
```bash
csvlink examples/restaurant-1.csv examples/restaurant-2.csv \
              --config_file=config.json
```

**Your config file may look like this:**

```json
{
  "field_names_1": ["name", "address", "city", "cuisine"],
  "field_names_2": ["restaurant", "street", "city", "type"],
  "field_definition" : [{"field" : "name", "type" : "String"},
                        {"field" : "address", "type" : "String"},
                        {"field" : "city", "type" : "String",
                         "Has Missing" : true},
                        {"field" : "cuisine", "type" : "String",
                         "Has Missing" : true}],
  "output_file": "examples/output.csv",
  "skip_training": false,
  "training_file": "training.json",
  "sample_size": 150000,
  "recall_weight": 2
}
```

#### To use `csvlink` you absolutely need:

  * `input` two CSV file names to join together

Either
  * `--config_file` Path to configuration file.

Or
  * `--field_names_1` List of column names in first file for dedupe to pay attention to
  * `--field_names_2` List of column names in second file for dedupe to pay attention to

#### You may also need:

  * `--output_file OUTPUT_FILE`
                        CSV file to store deduplication results (default:
                        None)
  * `--inner_join`          Only return matches between datasets
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
  * `-d`, `--delimiter`
                        Delimiting character of the input CSV file (default: ,)
  * `-h`, `--help`            show help message and exit

## Training

The _secret sauce_ of csvdedupe is human input. In order to figure out the best rules to deduplicate a set of data, you must give it a set of labeled examples to learn from.

The more labeled examples you give it, the better the deduplication results will be. At minimum, you should try to provide __10 positive matches__ and __10 negative matches__.

The results of your training will be saved in a JSON file ( __training.json__, unless specified otherwise with the `--training-file` option) for future runs of csvdedupe.

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

## Output
`csvdedupe` attempts to identify all the rows in the csv that refer to the same thing. Each group of
such records are called a cluster. `csvdedupe` returns your input file with an additional column called `Cluster ID`,
that either is the numeric id (zero-indexed) of a cluster of grouped records or an `x` if csvdedupe believes
the record doesn't belong to any cluster.

`csvlink` operates in much the same way as `csvdedupe`, but will flatten both CSVs in to one
output file similar to a SQL [OUTER JOIN](http://stackoverflow.com/questions/38549/difference-between-inner-and-outer-join) statement. You can use the `--inner_join` flag to exclude rows that don't match across the two input files, much like an INNER JOIN.


## Preprocessing
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

We chose the first option. While it is possible to do something more sophisticated, this option seems to work pretty well
for Latin alphabet languages.

## Testing

Unit tests of core csvdedupe functions
```bash
pip install -r requirements-test.txt
nosetests
```

## Community
* [Dedupe Google group](https://groups.google.com/forum/?fromgroups=#!forum/open-source-deduplication)
* IRC channel, #dedupe on irc.freenode.net

## Recipes

### Combining and deduplicating files from different sources.

Lets say we have a few sources of early childhood programs in Chicago and we'd like to get a canonical list.
Let's do it with `csvdedupe`, `csvkit`, and some other common command line tools.

#### Alignment and stacking
Our first task will be to align the files and have the same data in the same columns for stacking.

First, let's look at the headers of the files.

File 1
```console
> head -1 CPS_Early_Childhood_Portal_Scrape.csv
"Site name","Address","Phone","Program Name","Length of Day"
```

File 2
```console
> head -1 IDHS_child_care_provider_list.csv
"Site name","Address","Zip Code","Phone","Fax","IDHS Provider ID"
```

So, we'll have to add "Zip Code", "Fax", and "IDHS Provider ID"
to ```CPS_Early_Childhood_Portal_Scrape.csv```, and we'll have to add "Program Name",
"Length of Day" to ```IDHS_child_care_provider_list.csv```.

```console
> cd examples
> sed '1 s/$/,"Zip Code","Fax","IDHS Provider ID"/' CPS_Early_Childhood_Portal_Scrape.csv > input_1a.csv
> sed '2,$s/$/,,,/' input_1a.csv > input_1b.csv
```

```console
> sed '1 s/$/,"Program Name","Length of Day"/' IDHS_child_care_provider_list.csv > input_2a.csv
> sed '2,$s/$/,,/' input_2a.csv > input_2b.csv
```

Now, we reorder the columns in the second file to align to the first.

```console
> csvcut -c "Site name","Address","Phone","Program Name","Length of Day","Zip Code","Fax","IDHS Provider ID" \
         input_2b.csv > input_2c.csv
```

And we are finally ready to stack.

```console
> csvstack -g CPS_Early_Childhood_Portal_Scrape.csv,IDHS_child_care_provider_list.csv \
           -n source \
           input_1b.csv input_2c.csv > input.csv
```

#### Dedupe it!
And now we can dedupe

```console
> cat input.csv | csvdedupe --field_names "Site name" Address "Zip Code" Phone > output.csv
```

Let's sort the output by duplicate IDs, and we are ready to open it in your favorite spreadsheet program.

```console
> csvsort -c "Cluster ID" output.csv > sorted.csv
```

## Errors and Bugs

If something is not behaving intuitively, it is a bug, and should be reported.
Report it [here](https://github.com/dedupeio/csvdedupe/issues).

## Patches and Pull Requests
We welcome your ideas! You can make suggestions in the form of [github issues](https://github.com/dedupeio/csvdedupe/issues) (bug reports, feature requests, general questions), or you can submit a code contribution via a pull request.

How to contribute code:

- Fork the project.
- Make your feature addition or bug fix.
- Send us a pull request with a description of your work! Don't worry if it isn't perfect - think of a PR as a start of a conversation, rather than a finished product.

## Copyright and Attribution

Copyright (c) 2016 DataMade. Released under the [MIT License](https://github.com/dedupeio/csvdedupe/blob/master/LICENSE.md).
