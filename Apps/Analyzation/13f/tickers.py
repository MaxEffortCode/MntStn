import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re


def format_company_info(info):
    str_arr = info.split(" ")
    info_arr = []

    for word in str_arr:
        if "NASDAQ" in word:
            info_arr.append(word)
        
        if "NYSE" in word:
            try:
                ticker = re.findall(r'[A-Z]{1,5}\W[A-Z]{1,5}', word)
                #need to learn regex
                
                if len(ticker):
                    info_arr.append(f"{ticker} {len(ticker)}")
            
            except(ValueError):
                continue
    
    #print(info_arr)
    return info_arr

def get_source(url):
    """Return the source code for the provided URL. 

    Args: 
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html. 
    """

    try:
        text= "ALBEMARLECORP+stock"
        url = 'https://google.com/search?q=' + text
        
        # Fetch the URL data using requests.get(url),
        # store it in a variable, request_result.
        request_result=requests.get( url )
        
        # Creating soup from the fetched request
        soup = BeautifulSoup(request_result.text,
                                "html.parser")
        
        div = soup.find_all('div')

        for div in div:
            #we are running it through to many times
            if "NASDAQ" in div.getText():
                arrrr = format_company_info(div.getText())



            if "NYSE" in div.getText():
                arrrr = format_company_info(div.getText())

        
        print(arrrr)
        return "end function"
        
    except requests.exceptions.RequestException as e:
        print(f"error :  {e}")
