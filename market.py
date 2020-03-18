#!/usr/bin/env python3

import requests
import csv
from influxdb import InfluxDBClient
import creds
import sys

"""
Define a function to get the current information for a single stock symbol from the Alpha Vantage API
"""
def get_quote(symbol):

        # Specify the Alpha Vantage API URL and a friendly user-agent before hitting the API
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={creds.vantage_creds['api_key']}&datatype=csv"
        user_agent = 'Stock Market Graphing / https://github.com/ericoc/'
        headers = { 'User-Agent': user_agent}
        data = requests.get(url, headers=headers)
        data.raise_for_status()

        # If the API did not rate limit, write the CSV locally for parsing
        filename = f"{symbol}.csv"
        if 'Our standard API call frequency is 5 calls per minute' not in data.text:
            with open(filename, 'w') as f:
                f.write(data.text)

        # Read the CSV and return the row
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                return row


# Wrap this whole thing in a big try to catch any and all exceptions
try:

    # Connect to InfluxDB (with read-write credentials)
    client = InfluxDBClient(host=creds.db_creds_rw['host'], port=8086, username=creds.db_creds_rw['user'], password=creds.db_creds_rw['passwd'], database=creds.db_creds_rw['db'])

    # Loop through requested symbols
    for symbol in creds.symbols:

        # Get quote for the current symbol
        quote = get_quote(symbol)

        # Insert the latest price for the current symbol
        data = f"quotes,symbol={symbol} price={quote['price']}"
        insert_quote = client.write(data, params={'db': creds.db_creds_rw['db']}, protocol='line')
        if insert_quote != True:
            raise Exception(f"Stock symbol {symbol} ({quote['price']}) failed to insert")

# Print any exceptions
except Exception as e:
    sys.stderr.write(str(e))
    exit(1)

# Close the InfluxDB connection
finally:
    client.close()
