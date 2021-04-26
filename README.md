# Pedestrian Counting Reporting

This code uses the pedestrian count data provided by the City of Melbourne.  The data set is an hourly count of pedestrians
that have passed multiple sensors around the city.  Using the code you can report the top <i>n</i> pedestrian sites for a
particular day or month.  Command line arguments are provided to set the various runtime options.

The code can use a local copy of the dataset or one stored on AWS S3 storage.

## Installation

The code is written in python using V3.x.  To run, a python3 environment is required and `requirements.txt` is 
provided to install all necessary python packages.

To install run:

```
pip3 install -r requirements.txt
```

## Execution

To run the code, there are several command line arguments to define the operation of the code.

Below is the usage statement:

```
usage: python3 pedestrian_count.py [--help|-h] [--date|-d dd/mm/yyyy] [--month|-m mm/yyyy] [--topn|-n <num>] [--s3|-s <S3 URL>] [--write|-w]

optional arguments:
  --help  | -h            show this help message and exit
  --date  | -d dd/mm/yyyy Date to count pedestrians - dd/mm/yyyy
  --month | -m mm/yyyy    Month to count pedestrians - mm/yyyy
  --topn  | -n <num>      Top <num> pedestrian sites to list
  --s3    | -s <S3 URL>   S3 URL to data source file
  --write | -w            Flag to write results to a file 
```

The S3 URL to use to load the data is:

```
s3://sw-pedestrian-count/Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv
```

AWS credentials are to be hard-coded in the code (lines 19 & 20), but provided separately and not stored in a public GitHub repo.

## Design

Using the power of the python `pandas` package it is possible to perform complex and advanced data manipulation.  Therefore it made sense to utilise this package for this project.

The program is composed of several functions:

1.	`main()` - the main program to parse and validate command line arguments and then to call necessary data processing functions.
2.	`load_month()` - this function is used to load the dataset from either a local file, or S3 storage.  It is expected the input file is in CSV format.  To optimise loading and reduce memory the data is filtered to only load the required month of data.  For a local file it uses `pandas` filtering, while for S3 it uses the `select` query capability.  A `pandas dataframe` is returned by this function.
3.	`load_day()` - this function simply filters the dataset for the selected day and returns a new `dataframe`.
4.	`top_n()` - this function uses the power of `pandas` grouping, aggregation and sorting to select the top pedestrian site for the selected day or month.  A new `dataframe` is returned.
5. `write_output` - this functions writes the results in CSV format to a file if the command line argument is set.  If S3 is specified for the input dataset then the results file is written to the same S3 bucket.

## Testing

For a production version of such code unit tests could be written, using `pytest`, for each of the code functions to ensure they perform the correct operation.  A small dataset should be extracted to simplify the testing.  Testing could be performed manually by the programmer during development or `pytest` could be incorporated into the CI/CD pipeline.  Such unit tests would be ideal for regression testing as well to ensure any changes to the functions didn't change their behaviour.

In addition the final results could be set up as test results to actually test the integration of all the functions and ensure the correct results are output.  Again any changes to the code would be tested against the final test results to ensure changes aren't modifying the program's operational behaviour.