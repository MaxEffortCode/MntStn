import itertools
import time
import os
from Apps.Collection.src.api.sec_api import SecAPI
from Apps.Collection.src.helper import helper
from Settings.setup_logger import logging

logger = logging.getLogger(__name__)
sec_api = SecAPI()

# Setup years and quarters (1-4) of company filings to process
years = ["2020"]
quarters = ["1"]

file_counter_13f_hr = 0
file_counter_13f_hr_amendment = 0
file_counter_10k = 0
file_counter_10k_amendment = 0
file_counter_10Q = 0
file_counter_10Q_amendment = 0
file_counter_8k = 0

#
# Helper Methods
# ========================================================================================
def get_company_info_tuple_sec_form_crawler(line, qtr, yr):
    # 914208|Invesco Ltd.|3|2022-02-10|edgar/data/914208/0001209191-22-008399.txt
    split_line_company_info_array = line.strip().split("|")

    company_cik = split_line_company_info_array[0].strip()
    company_filing = split_line_company_info_array[2]

    company_info_tuple = (company_cik, company_filing, qtr, yr, split_line_company_info_array)
    return company_info_tuple
# ========================================================================================

for yr in years:
    for qtr in quarters:
        response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
        edgar_index_file_path= helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
        with open(edgar_index_file_path) as file:
            for line in itertools.islice(file, 11, None):
                company_info_tuple = get_company_info_tuple_sec_form_crawler(line, qtr, yr)

                if(company_info_tuple[1] == "13F-HR"):
                    file_counter_13f_hr += 1
                    logger.info(f"Processing 13F-HR for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_13f_hr_filing_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper().process_13f_hr(filing_response, company_info_tuple)
                elif(company_info_tuple[1] == "13F-HR/A"):
                    file_counter_13f_hr_amendment += 1
                    logger.info(f"Processing 13F-HR/A for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_13f_hr_filing_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper().process_13f_hr(filing_response, company_info_tuple)
                elif(company_info_tuple[1] == "10-K"):
                    file_counter_10k += 1
                    logger.info(f"Processing 10-K for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper.process_10k(filing_response, sec_api, company_info_tuple)
                elif(company_info_tuple[1] == "10-K/A"):
                    file_counter_10k_amendment += 1
                    logger.info(f"Processing 10-K/A for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper.process_10k(filing_response, sec_api, company_info_tuple)
                elif(company_info_tuple[1] == "10-Q"):
                    file_counter_10Q += 1
                    logger.info(f"Processing 10-Q for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper.process_10q(filing_response, sec_api, company_info_tuple)
                elif(company_info_tuple[1] == "10-Q/A"):
                    file_counter_10Q_amendment += 1
                    logger.info(f"Processing 10-Q/A for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                    time.sleep(1/10)
                    helper.process_10q(filing_response, sec_api, company_info_tuple)
                else:
                    #TODO: create case for untracked filings
                    continue

logger.info("Processed " + str(file_counter_13f_hr) + " 13F-HR files in master file.")
logger.info("Processed " + str(file_counter_13f_hr_amendment) + " 13F-HR/A files in master file.")
logger.info("Processed " + str(file_counter_10k) + " 10-K files in master file.")
logger.info("Processed " + str(file_counter_10k_amendment) + " 10-K/A files in master file.")
logger.info("Processed " + str(file_counter_10Q) + " 10-Q files in master file.")
logger.info("Processed " + str(file_counter_10Q_amendment) + " 10-Q/A files in master file.")
