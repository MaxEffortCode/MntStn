import itertools
import time
import os
import sys
from Apps.Collection.src.api.sec_api import SecAPI
from Apps.Collection.src.helper import helper
from Settings.setup_logger import logging

logger = logging.getLogger(__name__)
sec_api = SecAPI()

# Setup years and quarters (1-4) of company filings to process
years = ["2018", "2019", "2020", "2021", "2022"]
quarters = ["1", "2", "3", "4"]

file_counter_13f_hr = 0
file_counter_13f_hr_amendment = 0
file_counter_10k = 0
file_counter_10k_amendment = 0
file_counter_10Q = 0
file_counter_10Q_amendment = 0
file_counter_8k = 0
file_counter_untracked = 0

#
# Helper Methods
# ========================================================================================


def get_company_info_tuple_sec_form_crawler(line, qtr, yr):
    # 914208|Invesco Ltd.|3|2022-02-10|edgar/data/914208/0001209191-22-008399.txt
    split_line_company_info_array = line.strip().split("|")

    company_cik = split_line_company_info_array[0].strip()
    company_filing = split_line_company_info_array[2]

    company_info_tuple = (company_cik, company_filing, qtr,
                          yr, split_line_company_info_array)
    return company_info_tuple
# ========================================================================================


class sec_form_crawler:
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.file_counter_13f_hr = 0
        self.file_counter_13f_hr_amendment = 0
        self.file_counter_10k = 0
        self.file_counter_10k_amendment = 0
        self.file_counter_10Q = 0
        self.file_counter_10Q_amendment = 0
        self.file_counter_8k = 0
        self.file_counter_untracked = 0

    def crawl_sec_forms(self):
        response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(self.quarter, self.year)
        edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(
            response, self.quarter, self.year)
        with open(edgar_index_file_path) as file:
            for line in itertools.islice(file, 11, None):
                try:
                    company_info_tuple = get_company_info_tuple_sec_form_crawler(
                        line, self.quarter, self.year)

                    if(company_info_tuple[1] == "13F-HR"):
                        self.file_counter_13f_hr += 1
                        logger.info(
                            f"Processing 13F-HR for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_13f_hr_filing_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper().process_13f_hr(filing_response, company_info_tuple)
                    elif(company_info_tuple[1] == "13F-HR/A"):
                        self.file_counter_13f_hr_amendment += 1
                        logger.info(
                            f"Processing 13F-HR/A for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_13f_hr_filing_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper().process_13f_hr(filing_response, company_info_tuple)
                    elif(company_info_tuple[1] == "10-K"):
                        self.file_counter_10k += 1
                        logger.info(
                            f"Processing 10-K for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_index_json_filing_response_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper.process_10k(
                            filing_response, sec_api, company_info_tuple)
                    elif(company_info_tuple[1] == "10-K/A"):
                        self.file_counter_10k_amendment += 1
                        logger.info(
                            f"Processing 10-K/A for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_index_json_filing_response_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper.process_10k(
                            filing_response, sec_api, company_info_tuple)
                    elif(company_info_tuple[1] == "10-Q"):
                        self.file_counter_10Q += 1
                        logger.info(
                            f"Processing 10-Q for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_index_json_filing_response_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper.process_10q(
                            filing_response, sec_api, company_info_tuple)
                    elif(company_info_tuple[1] == "10-Q/A"):
                        self.file_counter_10Q_amendment += 1
                        logger.info(
                            f"Processing 10-Q/A for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_index_json_filing_response_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper.process_10q(
                            filing_response, sec_api, company_info_tuple)
                    else:
                        self.file_counter_untracked += 1
                        logger.info(
                            f"Processing {company_info_tuple[1]} 'untracked' for : {company_info_tuple[0]}\n")
                        filing_response = sec_api.get_index_json_filing_response_for_company_api(
                            company_info_tuple[4])
                        time.sleep(1/10)
                        helper.process_untracked(
                            filing_response, sec_api, company_info_tuple)

                except Exception as e:
                    logger.error(
                        f"Error processing {company_info_tuple[1]} for : {company_info_tuple[0]}\n")
                    logger.error(e)
                    continue

            logger.info("Processed " + str(self.file_counter_13f_hr) +
                        " 13F-HR files in master file.")
            logger.info("Processed " + str(self.file_counter_13f_hr_amendment) +
                        " 13F-HR/A files in master file.")
            logger.info("Processed " + str(self.file_counter_10k) +
                        " 10-K files in master file.")
            logger.info("Processed " + str(self.file_counter_10k_amendment) +
                        " 10-K/A files in master file.")
            logger.info("Processed " + str(self.file_counter_10Q) +
                        " 10-Q files in master file.")
            logger.info("Processed " + str(self.file_counter_10Q_amendment) +
                        " 10-Q/A files in master file.")
            logger.info("Processed " + str(self.file_counter_untracked) +
                        " untracked files in master file.")


if __name__ == "__main__":
    year = sys.argv[1]
    quarter = sys.argv[2]
    
    sec_form_crawler_2020_1 = sec_form_crawler(year, quarter)
    sec_form_crawler_2020_1.crawl_sec_forms()