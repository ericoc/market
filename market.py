#!/usr/bin/env python3

import requests
import csv
import pymysql
import creds


"""
Define a function to get the current information for a single stock symbol from the Alpha Vantage API
"""
def get_quote(symbol):

        # Specify the Alpha Vantage API URL and a friendly user-agent before hitting the API
        url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + symbol + '&apikey=' + creds.vantage_creds['api_key'] + '&datatype=csv'
        user_agent = 'Stock Market Graphing / https://github.com/ericoc/'
        headers = { 'User-Agent': user_agent}
        data = requests.get(url, headers=headers)
        data.raise_for_status()

        # If the API did not rate limit, write the CSV locally for parsing
        filename = symbol + '.csv'
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

    # Connect to MySQL (with read-write credentials) and open a database cursor
    dbh = pymysql.connect(host=creds.db_creds_rw['host'], user=creds.db_creds_rw['user'], passwd=creds.db_creds_rw['passwd'], db=creds.db_creds_rw['db'])
    with dbh.cursor() as dbc:

        # Loop through requested symbols
        for symbol in creds.symbols:

            # Get quote for the current symbol
            quote = get_quote(symbol)

            # Create a query to insert the price for the current symbol with current timestamp
            insert_quote = ("INSERT INTO `quotes` (`time`, `symbol`, `price`)"
                            "VALUES (NOW(), %(symbol)s, %(price)s)")

            # Fill in the details and execute the query
            quote_values = {
                            'symbol': symbol,
                            'price': quote['price']
                            }
            dbc.execute(insert_quote, quote_values)

    # End database cursor, commit the transaction, and close the MySQL connection
    dbh.commit()
    dbh.close()

# Print any exceptions
except Exception as e:
    print(e)
