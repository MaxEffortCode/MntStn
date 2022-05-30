import itertools
import time
import os
from Apps.Collection.src.api.sec_api import SecAPI
from Apps.Collection.src.helper import helper
from Settings.setup_logger import logging


#unix socket on local?

logger = logging.getLogger(__name__)
sec_Api = SecAPI()

#TODO: refactor
yr = '2022'
qtr = '1'

response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
#creates giant list with ALL company filing from the qrt
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
fileCounter13fhr = 0
fileCounter10q = 0
fileCounter10k = 0
fileCounter8k = 0
fileCounter11k = 0
fileCounter4 = 0
fileCounterUntracked = 0


def write_untracked_file_type(file_type):
    path = f"{os.path.dirname(__file__)}/resources/untracked_files"
    #f = open(f"{path}/untracked_filing_types.txt", "r")
    with open(f"{path}/untracked_filing_types.txt") as file:
        if file_type not in file.read().splitlines():
            file = open(f"{path}/untracked_filing_types.txt", "a")
            file.write(f"{file_type}\n")
    file.close()

#"/home/max/MntStn/Apps/Collection/src/resources/edgar-full-index-archives/master-2022-QTR1-test.txt"
with open(edgarIndexFilePath) as file:
    for line in itertools.islice(file, 11, None):
        #914208|Invesco Ltd.|3|2022-02-10|edgar/data/914208/0001209191-22-008399.txt
        splitLineCompanyInfo = line.strip().split("|")    
        companyName = splitLineCompanyInfo[1].strip()
        companyName = companyName.replace(',', '')
        companyName = companyName.replace(' ', '-')
        companyFiling = splitLineCompanyInfo[2]


        if(companyFiling == "8-K"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 8-K for : {companyName}\n")
            filingFile = sec_Api.get8KFilingForCompanyApi(splitLineCompanyInfo)
            #https://www.sec.gov/Archives/edgar/data/1000045/000095017022000296/index.json
            #https://www.sec.gov/Archives/edgar/data/1000045/000095017022000296/nick-20220113.xsd
            print(filingFile)
            time.sleep(1/10)
            helper.process_8k(filingFile, sec_Api, companyInfoTuple)
            fileCounter8k+=1
        
        
        elif(companyFiling == "10-K"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr)
            fileCounter10k += 1
            logger.info(f"Processing 10-K for : {companyName}\n")
            filingFile = sec_Api.get10kFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            #sec api is the returned object from a get request direct to sec.gov
            helper.process_10k(filingFile, sec_Api, companyInfoTuple)
        
        
        elif(companyFiling == "10-K/A"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter10q += 1
            logger.info(f"Processing NT 10-K/A for : {companyName}\n")
            filingFile = sec_Api.get10KAFilingForCompanyApi(splitLineCompanyInfo)
            print(filingFile.content)
            time.sleep(1/10)
            helper.process_10KA(filingFile, sec_Api, companyInfoTuple)
            pass
        
        
        elif(companyFiling == "10-Q"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter10q += 1
            logger.info(f"Processing 10Q for : {companyName}\n")
            filingFile = sec_Api.get10QFilingForCompanyApi(splitLineCompanyInfo)
            print(filingFile.content)
            time.sleep(1/10)
            helper.process_10q(filingFile, sec_Api, companyInfoTuple)
        
        elif(companyFiling == "NT 10-K"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter10q += 1
            logger.info(f"Processing NT 10k for : {companyName}\n")
            filingFile = sec_Api.get10NT10KFilingForCompanyApi(splitLineCompanyInfo)
            print(filingFile.content)
            time.sleep(1/10)
            helper.process_NT10k(filingFile, sec_Api, companyInfoTuple)
            

        elif(companyFiling == "11-K"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 11-K for : {companyName}\n")
            filingFile = sec_Api.get8KFilingForCompanyApi(splitLineCompanyInfo)
            print(f"filing file: {filingFile}")
            #time.sleep(3)
            helper.process_11k(filingFile, sec_Api, companyInfoTuple)
            fileCounter11k+=1
            pass
        
        elif(companyFiling == "13F-HR"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 13F-HR for : {companyName}\n")
            filingFile = sec_Api.get13FHRFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            helper().process_13f_hr(filingFile, companyInfoTuple)
            #pass in to sql helper companyInfoTuple
        
        elif(companyFiling == "SC 13D"):
            pass
        
        elif(companyFiling == "SC 13D/A"):
            pass
        
        elif(companyFiling == "SC 13G/A"):
            pass
        
        elif(companyFiling == "24F-2NT"):
            pass
        
        elif(companyFiling == "497"):
            pass
        
        elif(companyFiling == "N-CEN/A"):
            pass
        
        elif(companyFiling == "N-CEN"):
            pass
        
        elif(companyFiling == "NPORT-P"):
            pass
        
        elif(companyFiling == "4"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter4 += 1
            logger.info(f"Processing 4 for : {companyName}\n")
            filingFile = sec_Api.get4FilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            helper.process_4(filingFile, sec_Api, companyInfoTuple)
            pass
        
        elif(companyFiling == "4/A"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter4 += 1
            logger.info(f"Processing 4A for : {companyName}\n")
            filingFile = sec_Api.get4AFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            helper.process_4A(filingFile, sec_Api, companyInfoTuple)
            pass
        
        elif(companyFiling == "S-8 POS"):
            pass
        
        elif(companyFiling == "24F-2NT"):
            pass
        
        elif(companyFiling == "UPLOAD"):
            pass
        
        elif(companyFiling == "CORRESP"):
            pass
        
        elif(companyFiling == "X-17A-5"):
            pass
        
        elif(companyFiling == "DEF 14A"):
            pass
        
        
        elif(companyFiling == "SUPPL"):
            pass
        
        elif(companyFiling == "FWP"):
            pass
        
        elif(companyFiling == "6-K"):
            pass
        
        elif(companyFiling == "40-F"):
            pass
        
        else:
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounterUntracked += 1
            logger.info(f"Untracked for : {companyName}\n\
                with filing: {companyInfoTuple[1]}")
            write_untracked_file_type(companyInfoTuple[1])
            time.sleep(1/15)

        


logger.info("Processed " + str(fileCounter13fhr) + " 13F-HR files in master file.")
logger.info("Processed " + str(fileCounter10k) + " 10k files in master file.")
logger.info("Processed " + str(fileCounter10q) + " 10q files in master file.")
logger.info("Processed " + str(fileCounter8k) + " 8k files in master file.")