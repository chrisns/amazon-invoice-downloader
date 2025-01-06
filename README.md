> Modified version to presume you've got chrome running already logged in to your amazon account with remote debug enabled at port `9223` and interested in `amazon.co.uk`

# Amazon Invoice Downloader

[![PyPI - Version](https://img.shields.io/pypi/v/amazon-invoice-downloader.svg)](https://pypi.org/project/amazon-invoice-downloader)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/amazon-invoice-downloader.svg)](https://pypi.org/project/amazon-invoice-downloader)

-----

**Table of Contents**

- [Amazon Invoice Downloader](#amazon-invoice-downloader)
  - [What it does](#what-it-does)
  - [Usage](#usage)
  - [License](#license)

## What it does


This program `amazon-invoice-downloader.py` is a utility script that uses the [Playwright](https://playwright.dev/) library to spin up a Chromium instance and automate the process of downloading invoices for Amazon purchases within a specified date range. The script logs into Amazon using the provided email and password, navigates to the "Returns & Orders" section, and retrieves invoices for the specified year or date range.

The user can provide their Amazon login credentials either through command line arguments (--email=<email> --password=<password>) or as environment variables ($AMAZON_EMAIL and $AMAZON_PASSWORD).

The script accepts the date range either as a specific year (--year=<YYYY>) or as a date range (--date-range=<YYYYMMDD-YYYYMMDD>). If no date range is provided, the script defaults to the current year.

Once the invoices are retrieved, they are saved as PDF files in a local "downloads" directory. The filename of each PDF is formatted as `YYYYMMDD_<total>_amazon_<orderid>.pdf`, where YYYYMMDD is the date of the order, total is the total amount of the order (with dollar signs and commas removed), and orderid is the unique Amazon order ID.

The program has a built-in "human latency" function, sleep(), to mimic human behavior by introducing random pauses between certain actions. This can help prevent the script from being detected and blocked as a bot by Amazon.

The script will skip downloading a file if it already exists in the `./downloads` directory.


## Usage

```console
$ /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223 --remote-debugging-address=0.0.0.0
$ hatch run pip install -e .
$ hatch run amazon-invoice-downloader --year 2023

```console
$ amazon-invoice-downloader -h
Amazon Invoice Downloader

Usage:
  amazon-invoice-downloader.py \
    [--year=<YYYY> | --date-range=<YYYYMMDD-YYYYMMDD>]
  amazon-invoice-downloader.py (-h | --help)

Date Range Options:
  --date-range=<YYYYMMDD-YYYYMMDD>  Start and end date range
  --year=<YYYY>            Year, formatted as YYYY  [default: <CUR_YEAR>].

Options:
  -h --help                Show this screen.

Examples:
  amazon-invoice-downloader.py --year=2022  # This uses env vars $AMAZON_EMAIL and $AMAZON_PASSWORD
  amazon-invoice-downloader.py --date-range=20220101-20221231
  amazon-invoice-downloader.py  # Defaults to current year
  amazon-invoice-downloader.py --year=2022
  amazon-invoice-downloader.py --date-range=20220101-20221231
```


## License

`amazon-invoice-downloader` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
