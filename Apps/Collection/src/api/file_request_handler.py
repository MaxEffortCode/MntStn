import os
import itertools
import time
import sys
import csv
from sec_api import SecAPI
from Settings.setup_logger import logging
from Apps.Collection.src.helper import helper

logger = logging.getLogger(__name__)
sec_api = SecAPI()

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

    def download_master_edgar_index_file(self):
        response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(self.quarter, self.year)
        edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(
            response, self.quarter, self.year)
        
        
    def get_file(self, cik=None, filing_type=None):
        if cik is None:
            cik = self.cik
        #check if the directory exists for Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}
        #if it does not exist create it
        if not os.path.exists(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}"):
            os.makedirs(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}")
        
        #get edgar index file
        with open(self.edgar_path) as file:
            #save all lines that match the cik
            lines = [line for line in file if cik in line.split("|")[0]]
            for line in lines:
                if filing_type is None:
                    continue
                if line.split("|")[2] != filing_type:
                    lines.remove(line)
            
        for line in lines:
            company_info_tuple = helper.get_company_info_tuple(line, self.quarter, self.year)
            if(company_info_tuple[1] == "13F-HR"):
                logger.info(
                    f"Processing 13F-HR for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_13f_hr_filing_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper().process_13f_hr(filing_response, company_info_tuple)
            elif(company_info_tuple[1] == "13F-HR/A"):
                logger.info(
                    f"Processing 13F-HR/A for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_13f_hr_filing_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper().process_13f_hr(filing_response, company_info_tuple)
            elif(company_info_tuple[1] == "10-K"):
                logger.info(
                    f"Processing 10-K for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_index_json_filing_response_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper.process_10k(
                    filing_response, sec_api, company_info_tuple)
            elif(company_info_tuple[1] == "10-K/A"):
                logger.info(
                    f"Processing 10-K/A for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_index_json_filing_response_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper.process_10k(
                    filing_response, sec_api, company_info_tuple)
            elif(company_info_tuple[1] == "10-Q"):
                logger.info(
                    f"Processing 10-Q for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_index_json_filing_response_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper.process_10q(
                    filing_response, sec_api, company_info_tuple)
            elif(company_info_tuple[1] == "10-Q/A"):
                logger.info(
                    f"Processing 10-Q/A for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_index_json_filing_response_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper.process_10q(
                    filing_response, sec_api, company_info_tuple)
            else:
                logger.info(
                    f"Processing {company_info_tuple[1]} 'untracked' for : {company_info_tuple[0]}\n")
                filing_response = sec_api.get_index_json_filing_response_for_company_api(
                    company_info_tuple[4])
                time.sleep(1/10)
                helper.process_untracked(
                    filing_response, sec_api, company_info_tuple)

        #add in exception handling
        
        #return the file path

if __name__ == "__main__":
    file_req_handler = FileReqHandler("2018", "1", "1000045")
    
    #get the file
    file_req_handler.get_file()
    
            