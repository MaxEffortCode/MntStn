from asyncio.log import logger
from numpy import greater
import requests
import urllib
import pandas as pd
import csv
import time
import random


def get_shares_from_yahoo(cusip, try_number = 1):
    time.sleep(1/10)
    url = f'https://query1.finance.yahoo.com/v1/finance/search?q={cusip}'
    headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.example'  # This is another valid field
    }
    
    request_result=requests.get(url, headers=headers)
    logger.info(f"Getting ticker for {cusip} at {url}")

    try:
        return f"{request_result.json()['quotes']}"
    
    except (KeyError, IndexError) as e:
        return None
    
    except (requests.exceptions.ConnectionError, ValueError) as e:
        time.sleep(2**try_number + random.random()*0.01) 
        try_number += 1
        if try_number >= 20:
            return None
        
    return get_shares_from_yahoo(cusip, try_number)