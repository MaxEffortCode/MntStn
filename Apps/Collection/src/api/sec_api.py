import requests
import logging
import time
from Settings.setup_logger import logging

LOGGER = logging.getLogger(__name__)

# Current max request rate: 10 requests/second per SEC - https://www.sec.gov/os/accessing-edgar-data 
class SecAPI:
    def __init__(self):
        self.header = {'Host': 'www.sec.gov', 'Connection': 'close',
         'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
         }
        self.baseUrl = ("https://www.sec.gov")
        # Current max request rate: 10 requests/second per SEC - https://www.sec.gov/os/accessing-edgar-data 

    def getMasterEdgarIndexFileByQtrAndYrApi(self, qtrNumber, year):
        url = f"{self.baseUrl}/Archives/edgar/full-index/{year}/QTR{qtrNumber}/master.idx"
        response = requests.get(url, headers=self.header)  
        LOGGER.info(f"Performing GET on: {url}")
        return response

    def get13FHRFilingForCompanyApi(self, companyInfo):
        url = f"{self.baseUrl}/Archives/{companyInfo[4]}"
        response = requests.get(url, headers=self.header)
        LOGGER.info(f"Performing GET on: {url}")
        return response

    def get10kFilingForCompanyApi(self, companyInfo):
        url = f"{self.baseUrl}/Archives/{companyInfo[4]}"
        url = url.replace('-','').replace('.txt', '/index.json')
        response = requests.get(url, headers=self.header)
        LOGGER.info(f"Performing GET on: {url}")
        return response

    def get10kFilingXmlSummaryByFileNameUrl(self, url):
        response = requests.get(url, headers=self.header)
        LOGGER.info(f"Performing GET on: {url}")
        return response