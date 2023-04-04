from asyncio.log import logger
from numpy import greater
import requests
import urllib
import pandas as pd
import csv
import time
import random


#class that works on finding and appending tickers
class Ticker:
    def __init__(self):
        




def get_cik_ticker_to_csv_from_sec(save_file = 'cik_ticker.csv', url = f'https://www.sec.gov/include/ticker.txt'):
    url = f'https://www.sec.gov/include/ticker.txt'
    
    headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.example'  # This is another valid field
    }
    
    request_result=requests.get(url, headers=headers)
    logger.info(f"Getting cik_ticker list at {url}")
    
    open('cik_ticker.txt', 'wb').write(request_result.content)
    
    with open('cik_ticker.txt', 'r') as txt_file:
        with open('cik_ticker.csv', 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['ticker', 'cik'])
            for line in txt_file:
                line_split = line.split()
                csv_writer.writerow([line_split[0], line_split[1]])
    
    
    
    return 'cik_ticker.csv'
    

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
