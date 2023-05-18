import os
import itertools
import time
import sys
import csv
import traceback
from polyfuzz import PolyFuzz
#export PYTHONPATH=/media/max/2AB8BBD1B8BB99B1/MntStn:$PYTHONPATH
from sec_api import SecAPI
from Settings.setup_logger import logging
from Apps.Collection.src.helper import helper
from Apps.Collection.src.organizers.master_index_parser import master_index_parser

logger = logging.getLogger(__name__)
sec_api = SecAPI()

class FileReqHandler:
    #maybe we should just instantiate it using the year and quarter
    #and then have a method that takes in the cik and filing type
    #along with a method that takes in the company name or ticker
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{year}/{quarter}/models/c_name_model")
        
    def __repr__(self):
        return f"FileReqHandler({self.year}, {self.quarter})"
    
    def update_year(self, year):
        self.year = year
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{self.quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{year}/{self.quarter}/models/c_name_model")
    
    def update_quarter(self, quarter):
        self.quarter = quarter
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{self.year}-QTR{quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{self.year}/{quarter}/models/c_name_model")
        
    def update_cik(self, cik):
        self.cik = cik
    
    def update_filing_type(self, filing_type):
        self.filing_type = filing_type
    
    def update_model(self, model_path):
        model = PolyFuzz.load(model_path)
        self.model = model

    def download_master_edgar_index_file(self):
        response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(self.quarter, self.year)
        edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(
            response, self.quarter, self.year)
        
        
    def get_file_cik(self, cik, filing_type=None):
        #check if the directory exists for Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}
        #if it does not exist create it
        if not os.path.exists(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}"):
            os.makedirs(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}")
        
        #CIK|Company Name|Form Type|Date Filed|Filename

        #get edgar index file
        with open(self.edgar_path) as file:
            #save all lines that match the cik
            lines = [line for line in file if cik in line.split("|")[0]]
            for line in lines:
                if filing_type is None:
                    continue
                if line.split("|")[2] != filing_type:
                    lines.remove(line)
        
        #need to add a list to store the file paths
        file_paths = []
        try: 
            for line in lines:
                company_info_tuple = helper.get_company_info_tuple(line, self.quarter, self.year)
                if(company_info_tuple[1] == "13F-HR"):
                    logger.info(
                        f"Processing 13F-HR for : {company_info_tuple[0]}\n")
                    #goes to sec page and sets filing_response to the sec response
                    filing_response = sec_api.get_13f_hr_filing_for_company_api(
                        company_info_tuple[4])
                    time.sleep(1/10)
                    file_path = helper().process_13f_hr(filing_response, company_info_tuple)
                    file_paths.append(file_path)
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
            
        except Exception as e:
            logger.error(f"Error processing filing for {company_info_tuple[0]}")
            logger.error(e)
            logger.error(traceback.format_exc())
            
        #return the file path
    
    def get_file_company_name(self, company_name, filing_type=None):
        search_term = [company_name]
        result = self.model.transform(search_term)
        result = result['TF-IDF'].values[0][1]
        print(result)
        with open(self.edgar_path) as file:
            #save all lines that match the cik
            lines = [line for i, line in enumerate(file) if i >= 14 and result.upper() in line.split("|")[1]]
            for line in lines:
                if filing_type is None:
                    continue
                if line.split("|")[2] != filing_type:
                    lines.remove(line)
        
        print(f"Found {len(lines)} filings for {company_name}")
        for line in lines:
            print(f"Processing {line}")
        
        return lines
        
        
        

if __name__ == "__main__":
    file_req_handler = FileReqHandler("2018", "2")
    #file_req_handler.get_file_cik("1000045", "13F-HR")
    file_req_handler.get_file_company_name("NICHOLAS FINANCIAL INC")

            