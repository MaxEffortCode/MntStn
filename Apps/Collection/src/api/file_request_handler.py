import os
import sys
import csv

class FileReqHandler:
    def __init__(self, year, quarter, cik, filing_type=None):
        self.year = year
        self.quarter = quarter
        self.cik = cik
        self.filing_type = filing_type
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{quarter}.txt"

    def __repr__(self):
        return f"FileReqHandler({self.year}, {self.quarter})"
    
    def update_year(self, year):
        self.year = year
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{self.quarter}.txt"
    
    def update_quarter(self, quarter):
        self.quarter = quarter
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{self.year}-QTR{quarter}.txt"
    
    def update_cik(self, cik):
        self.cik = cik
        
    def get_file(self, cik, filing_type=None):
        #check if the directory exists for Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}
        #if it does not exist create it
        if not os.path.exists(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}"):
            os.makedirs(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}")
