# SPDX-FileCopyrightText: 2023-present David C Wang <dcwangmit01@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Amazon Invoice Downloader

Usage:
  amazon-invoice-downloader.py \
    [--email=<email> --password=<password>] \
    [--year=<YYYY> | --date-range=<YYYYMMDD-YYYYMMDD>]
  amazon-invoice-downloader.py (-h | --help)

Login Options:
  --email=<email>          Amazon login email  [default: $AMAZON_EMAIL].
  --password=<password>    Amazon login password  [default: $AMAZON_PASSWORD].

Date Range Options:
  --date-range=<YYYYMMDD-YYYYMMDD>  Start and end date range
  --year=<YYYY>            Year, formatted as YYYY  [default: <CUR_YEAR>].

Options:
  -h --help                Show this screen.

Examples:
  amazon-invoice-downloader.py --year=2022  # This uses env vars $AMAZON_EMAIL and $AMAZON_PASSWORD
  amazon-invoice-downloader.py --date-range=20220101-20221231
  amazon-invoice-downloader.py --email=user@example.com --password=secret  # Defaults to current year
  amazon-invoice-downloader.py --email=user@example.com --password=secret --year=2022
  amazon-invoice-downloader.py --email=user@example.com --password=secret --date-range=20220101-20221231
"""

from amazon_invoice_downloader.__about__ import __version__

from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime
import random
import time
import os
import sys
from docopt import docopt


def sleep():
    # Add human latency
    # Generate a random sleep time between 3 and 5 seconds
    sleep_time = random.uniform(2, 5)
    # Sleep for the generated time
    time.sleep(sleep_time)


def run(playwright, args):
    email = args.get('--email')
    if email == '$AMAZON_EMAIL':
        email = os.environ.get('AMAZON_EMAIL')

    password = args.get('--password')
    if password == '$AMAZON_PASSWORD':
        password = os.environ.get('AMAZON_PASSWORD')
    
    # date_format = args.get('--email')
    # if date_format == '$AMAZON_DATE_FORMAT':
    #     date_format = os.environ.get('AMAZON_DATE_FORMAT')
    # # date_format = "%B %d, %Y"
    # date_format = "%d %B %Y"
    # Parse date ranges int start_date and end_date
    if args['--date-range']:
        start_date, end_date = args['--date-range'].split('-')
    elif args['--year'] != "<CUR_YEAR>":
        start_date, end_date = args['--year'] + "0101", args['--year'] + "1231"
    else:
        year = str(datetime.now().year)
        start_date, end_date = year + "0101", year + "1231"
    start_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    # Debug
    # print(email, password, start_date, end_date)

    # Ensure the location exists for where we will save our downloads
    target_dir = os.getcwd() + "/" + "downloads"
    os.makedirs(target_dir, exist_ok=True)

    # Create Playwright context with Chromium
    # browser = playwright.chromium.launch(headless=False)
    # browser = playwright.chromium.launch_persistent_context(headless=False, channel="chrome", user_data_dir="/Users/cns/Library/Application Support/Google/Chrome")
    # context = browser.new_context()
    browser = playwright.chromium.connect_over_cdp("http://localhost:9223")
    context = browser.contexts[0]

    page = context.new_page()
    page.goto("https://www.amazon.co.uk/gp/css/order-history")


    # page.wait_for_selector('a >> text=Returns & Orders', timeout=0).click()
    # sleep()

    # Get a list of years from the select options
    select = page.locator('select#time-filter')
    # select = page.get_by_role("select", name="timeFilter").click()
    years = select.inner_text().split("\n")  # skip the first two text options

    # Filter years to include only numerical years (YYYY)
    years = [year for year in years if year.isnumeric()]

    # Filter years to the include only the years between start_date and end_date inclusively
    years = [year for year in years if start_date.year <= int(year) <= end_date.year]
    years.sort(reverse=True)

    # Year Loop (Run backwards through the time range from years to pages to orders)
    for year in years:
        # Select the year in the order filter
        page.locator('span.a-dropdown-container').click()  # Time Range Dropdown Filter
        page.get_by_role("option", name=year).click()  # Select the year (descending order, most recent first)
        # sleep()
        page.wait_for_selector('ul.a-pagination')
        # Page Loop
        first_page = True
        done = False
        while not done:
            # Go to the next page pagination, and continue downloading
            #   if there is not a next page then break
            try:
                if first_page:
                    first_page = False
                else:
                    page.locator('ul.a-pagination li.a-last a').click()
                # sleep()  # sleep after every page load
            except TimeoutError:
                # There are no more pages
                break

            # Order Loop
            page.wait_for_selector('ul.a-pagination')
            page.wait_for_selector('.js-order-card .yohtmlc-order-id .value')
            order_cards = page.locator(".js-order-card")
            for order_card in order_cards.all():
                # Parse the order card to create the date and file_name
                spans = order_card.locator("span").all()
                date = datetime.strptime(spans[1].inner_text(), "%d %B %Y")
                total = spans[3].inner_text().replace("$", "").replace(",", "").replace("£", "")  # remove dollar sign and commas
                # orderid = spans[9].inner_text()
                orderid = order_card.locator(".yohtmlc-order-id .value").inner_text()
                date_str = date.strftime("%Y%m%d")

                if date > end_date:
                    continue
                elif date < start_date:
                    done = True
                    break

                detail_page = context.new_page()
                detail_page.goto(f"https://www.amazon.co.uk/gp/shared-cs/ajax/invoice/invoice.html?orderId={orderid}&relatedRequestId=NEEDED")

                pdfs = detail_page.locator("xpath=//a[contains(@href,'.pdf')]").all()
                if len(pdfs) == 0:
                    print ("No pdfs found for order", orderid)
                    detail_page.close()
                    continue
                pdf_i = 0
                for pdf in pdfs:
                    pdf_i += 1
                    file_name = f"{target_dir}/{date_str}_{total}_amazon_{orderid}_{pdf_i}.pdf"
                    if os.path.isfile(file_name):
                        print(f"File [{file_name}] already exists")
                        continue
                    with detail_page.expect_download() as download_info:
                        pdf.click(modifiers=["Alt", ])
                    download = download_info.value
                    download.save_as(file_name)
                detail_page.close()

    # Close the browser
    context.close()
    # browser.close()


def amazon_invoice_downloader():
    args = docopt(__doc__)

    with sync_playwright() as playwright:
        run(playwright, args)
