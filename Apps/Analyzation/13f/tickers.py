from asyncio.log import logger
from numpy import greater
import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import csv
import time
import random

def get_ticker_from_yahoo(cusip, try_number = 1):
    time.sleep(1/10)
    url = f'https://query1.finance.yahoo.com/v1/finance/search?q={cusip}'
    headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.example'  # This is another valid field
    }
    
    request_result=requests.get(url, headers=headers)
    logger.info(f"Getting ticker for {cusip} at {url}")

    try:
        return f"{request_result.json()['quotes'][0]['symbol']}"
    
    except (KeyError, IndexError) as e:
        return None
    
    except (requests.exceptions.ConnectionError, ValueError) as e:
        time.sleep(2**try_number + random.random()*0.01) 
        try_number += 1
        if try_number >= 20:
            return None
        
        return get_ticker_from_yahoo(cusip, try_number)

def get_ticker_from_vanguard(cusip, try_number = 1):
    time.sleep(1/2)
    url = f'https://investor.vanguard.com/investment-tools/calculator-tools/marketData?query={cusip}'
    request_result=requests.get( url )
    logger.info(f"Getting ticker for {cusip} at {url}")
    
    try:
        return f"{request_result.json()['result']['symbol']}"
    
    except KeyError as e:
        return None
    
    except (requests.exceptions.ConnectionError, ValueError) as e:
        time.sleep(2**try_number + random.random()*0.01) 
        try_number += 1
        if try_number >= 20:
            return None
        return get_ticker_from_vanguard(cusip, try_number)
    
        
def find_or_add_to_ticker_csv(cusip):
    with open('csv_with_ticker.csv', 'a', newline='') as csv_file:
        pass
    
    with open('csv_with_ticker.csv', 'r+', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        
        for row in csv_reader:
            if cusip.upper() in row[0]:
                return row[1]
        
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        ticker = get_ticker_from_vanguard(cusip)
        if ticker is None:
            ticker = get_ticker_from_yahoo(cusip)
        csv_writer.writerow([cusip.upper(), ticker])
        return ticker

def get_source(cusip):
    ticker = find_or_add_to_ticker_csv(cusip)
    return ticker
