import os
import time
import traceback
import time
import pickle
from polyfuzz import PolyFuzz
#export PYTHONPATH=/media/max/2AB8BBD1B8BB99B1/MntStn:$PYTHONPATH

from sec_api import SecAPI
from Settings.setup_logger import logging
from Apps.Collection.src.helper import helper
from Apps.Collection.src.organizers.master_index_parser import master_index_parser


logger = logging.getLogger(__name__)
sec_api = SecAPI()

def get_lines_from_file(file_path, line_numbers):
    lines = []

    with open(file_path, 'r') as file:
        for line_num in line_numbers:
            file.seek(0)  # Reset the file position indicator to the beginning of the file
            for _ in range(line_num - 1):
                file.readline()  # Skip preceding lines
            line = file.readline()  # Read the desired line
            lines.append(line)

    return lines

def file_processor(company_info_tuple, cik, fileRequestHandler):
    file_path = None

    if(company_info_tuple[1] == "13F-HR"):
        logger.info(
            f"Processing 13F-HR for : {company_info_tuple[0]}\n")
        #if the file already exists, just send the file
        if os.path.exists(f"Apps/Collection/src/resources/{fileRequestHandler.get_year()}/{fileRequestHandler.get_quarter()}/companies/{cik}/filings/13F-HR-data.csv.gz"):
            file_path = (f"Apps/Collection/src/resources/{fileRequestHandler.get_year()}/{fileRequestHandler.get_quarter()}/companies/{cik}/filings/13F-HR-data.csv.gz")
            print(f"\n****found file is {file_path}****\n")
            return file_path
            

        #goes to sec page and sets filing_response to the response from edgar
        filing_response = sec_api.get_13f_hr_filing_for_company_api(
            company_info_tuple[4])
        
        file_path = helper().process_13f_hr(filing_response, company_info_tuple)
        print(f"\n****File path is {file_path}****\n")
        return file_path

    elif(company_info_tuple[1] == "13F-HR/A"):
        logger.info(
            f"Processing 13F-HR/A for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_13f_hr_filing_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        file_path = helper().process_13f_hr(filing_response, company_info_tuple)
        #helper().process_13f_hr(filing_response, company_info_tuple)
    elif(company_info_tuple[1] == "10-K"):
        logger.info(
            f"Processing 10-K for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_index_json_filing_response_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        helper.process_10k(
            filing_response, sec_api, company_info_tuple)
    elif(company_info_tuple[1] == "10-K/A"):
        logger.info(
            f"Processing 10-K/A for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_index_json_filing_response_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        helper.process_10k(
            filing_response, sec_api, company_info_tuple)
    elif(company_info_tuple[1] == "10-Q"):
        logger.info(
            f"Processing 10-Q for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_index_json_filing_response_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        helper.process_10q(
            filing_response, sec_api, company_info_tuple)
    elif(company_info_tuple[1] == "10-Q/A"):
        logger.info(
            f"Processing 10-Q/A for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_index_json_filing_response_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        helper.process_10q(
            filing_response, sec_api, company_info_tuple)
    else:
        logger.info(
            f"Processing {company_info_tuple[1]} 'untracked' for : {company_info_tuple[0]}\n")
        filing_response = sec_api.get_index_json_filing_response_for_company_api(
            company_info_tuple[4])
        #time.sleep(1/10)
        helper.process_untracked(
            filing_response, sec_api, company_info_tuple)



class EdgarIndexFileHandler:
    def __init__(self):
        pass
    
    def get_pickled_index(self, fileReqHandler):
        #check if the pickled index exists
        #if it does, return it
        if os.path.exists(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl"):
            with open(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl", 'rb') as f:
                return pickle.load(f)

        try:
            response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(fileReqHandler.get_quarter(), fileReqHandler.get_year())
            edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(
                response, fileReqHandler.get_quarter(), fileReqHandler.get_year())
            
            index = {}
            with open(edgar_index_file_path, 'r') as file:
                for line_num, line in enumerate(file, start=1):
                    number = line.split('|')[0]
                    if number in index:
                        index[number].append(line_num)
                    else:
                        index[number] = [line_num]

            with open(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl", 'wb') as f:
                pickle.dump(index, f)
            
            with open(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl", 'rb') as f:
                return pickle.load(f)


        except Exception as e:
            logger.error(f"Error getting pickled edgar index: {e}")
            traceback.print_exc()
            return False
    
    def search_index(self, fileReqHandler, cik, filing_type=None):
        #check if the pickled index exists
        #if it does, return it
        if os.path.exists(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl"):
            with open(f"Apps/Collection/src/resources/{fileReqHandler.get_year()}/{fileReqHandler.get_quarter()}/lookup/index.pkl", 'rb') as f:
                index = pickle.load(f)
        else:
            index = self.get_pickled_index(fileReqHandler)
        
        if cik in index:
            return index[cik]
        else:
            return False

        



class FileReqHandler:
    #maybe we should just instantiate it using the year and quarter
    #and then have a method that takes in the cik and filing type
    #along with a method that takes in the company name or ticker
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{year}/{quarter}/models/mnt_model")
        self.index_file_handler = EdgarIndexFileHandler()
        self.pickle_index = self.index_file_handler.get_pickled_index(self)
        
    def __repr__(self):
        return f"FileReqHandler({self.year}, {self.quarter})"
    
    def __str__(self):
        return f"FileReqHandler({self.year}, {self.quarter})"
    
    def get_pickle_index(self):
        return self.pickle_index

    def get_year(self):
        return self.year
    
    def get_quarter(self):
        return self.quarter
    
    def update_year(self, year):
        self.year = year
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{year}-QTR{self.quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{year}/{self.quarter}/models/mnt_model")
    
    def update_quarter(self, quarter):
        self.quarter = quarter
        self.edgar_path = f"Apps/Collection/src/resources/edgar-full-index-archives/master-{self.year}-QTR{quarter}.txt"
        self.model = PolyFuzz.load(f"Apps/Collection/src/resources/{self.year}/{quarter}/models/mnt_model")
        
    def update_cik(self, cik):
        self.cik = cik
    
    def update_filing_type(self, filing_type):
        self.filing_type = filing_type
    
    def update_model(self, model_path):
        model = PolyFuzz.load(model_path)
        self.model = model

    def get_file_cik(self, cik, filing_type=None):
        logger.info(f"\nGetting file for {cik} and filing type {filing_type}\n")

        #check if the directory exists for Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}
        #if it does not exist create it
        if not os.path.exists(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}"):
            os.makedirs(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}")
        
        #CIK|Company Name|Form Type|Date Filed|Filename

        #search the pickled index for the cik
        index_lines = self.index_file_handler.search_index(self, cik, filing_type)
        if index_lines is False:
            logger.info(f"\nNo filings found for {cik} and filing type {filing_type}\n")
            return False
        
        print(f"\nFound {len(index_lines)} filings for {cik} and filing type {filing_type}\n")
        print(f"\nThe lines are {index_lines}\n")
        
        #go to the index lines in the edgar index file
        lines = get_lines_from_file(self.edgar_path, index_lines)
        lines_user_requested = []
        if filing_type is None:
                lines = lines
        else:
            for line in lines:
                if line.split("|")[2] == filing_type:
                    lines_user_requested.append(line)

            lines = lines_user_requested
           
        
        print(f"\nThe lines are {lines}\n")


        #need to add a list to store the file paths
        file_paths = []
        try: 
            for line in lines:
                company_info_tuple = helper.get_company_info_tuple(line, self.quarter, self.year)
                if(company_info_tuple[1] == "13F-HR"):
                    logger.info(
                        f"Processing 13F-HR for : {company_info_tuple[0]}\n")
                    #if the file already exists, just send the file
                    if os.path.exists(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}/filings/13F-HR-data.csv.gz"):
                        file_paths.append(f"Apps/Collection/src/resources/{self.year}/{self.quarter}/companies/{cik}/filings/13F-HR-data.csv.gz")
                        print(f"\n****found file is {file_paths}****\n")
                        continue
                        

                    #goes to sec page and sets filing_response to the response from edgar
                    filing_response = sec_api.get_13f_hr_filing_for_company_api(
                        company_info_tuple[4])
                    
                    file_path = helper().process_13f_hr(filing_response, company_info_tuple)
                    print(f"\n****File path is {file_path}****\n")
                    file_paths.append(file_path)

                elif(company_info_tuple[1] == "13F-HR/A"):
                    logger.info(
                        f"Processing 13F-HR/A for : {company_info_tuple[0]}\n")
                    filing_response = sec_api.get_13f_hr_filing_for_company_api(
                        company_info_tuple[4])
                    time.sleep(1/10)
                    file_paths.append(helper().process_13f_hr(filing_response, company_info_tuple))
                    #helper().process_13f_hr(filing_response, company_info_tuple)
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
        return file_paths
    
    #lines = [line for i, line in enumerate(file) if i >= 14 and result.upper() in line.split("|")[1]]
    def get_file_company_name(self, company_name, filing_type=None):
        #begin timer
        start = time.time()
        search_term = [company_name.lower()]
        print(search_term)
        result = self.model.transform(search_term)
        print(f"Result: {result}")
        result = result['TF-IDF'].values[0][1]
        print(result)
        with open(self.edgar_path) as file:
            #find the first line that matches the result 
            #skip the first 14 lines
            cik = None
            for i, line in enumerate(file):
                if i >= 14:
                    if result.upper() in line.split("|")[1]:
                        cik = line.split("|")[0]
                        print(line)
                        break  
                else:
                    continue
        #end timer
        end = time.time()
        print(f"Time to find CIK: {end - start}")
        
        print(f"Found CIK: {cik} for {company_name}")

        return cik
        
        
        

if __name__ == "__main__":
    file_req_handler = FileReqHandler("2004", "1")

    pickled_index = file_req_handler.get_pickle_index()
    print(f"Pickled index is")
    irst2vals = [print(f"pickled_index[k] is {k}") for k in sorted(pickled_index.values())[300:309]]

    #file_req_handler.get_file_cik("1000045", "13F-HR")
    company_cik = file_req_handler.get_file_company_name("META GROUP INC")
    company_list = file_req_handler.get_file_cik(company_cik, "13F-HR")