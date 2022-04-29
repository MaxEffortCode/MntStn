import itertools
import time
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
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
fileCounter13fhr = 0
fileCounter10q = 0
fileCounter10k = 0
fileCounter8k = 0
fileCounter11k = 0


logger.info(f"{edgarIndexFilePath}")
#"/home/max/MntStn/Apps/Collection/src/resources/edgar-full-index-archives/master-2022-QTR1-test.txt"
with open(edgarIndexFilePath) as file:
    for line in itertools.islice(file, 11, None):
        #914208|Invesco Ltd.|3|2022-02-10|edgar/data/914208/0001209191-22-008399.txt
        splitLineCompanyInfo = line.strip().split("|")    
        companyName = splitLineCompanyInfo[1].strip()
        companyName = companyName.replace(',', '')
        companyName = companyName.replace(' ', '-')
        companyFiling = splitLineCompanyInfo[2]

        if(companyFiling == "13F-HR"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 13F-HR for : {companyName}\n")
            filingFile = sec_Api.get13FHRFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            helper().process_13f_hr(filingFile, companyInfoTuple)
            #pass in to sql helper companyInfoTuple


        elif(companyFiling == "10-K"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr)
            fileCounter10k += 1
            logger.info(f"Processing 10-K for : {companyName}\n")
            filingFile = sec_Api.get10kFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            #sec api is the returned object from a get request direct to sec.gov
            helper.process_10k(filingFile, sec_Api, companyInfoTuple)
        
        elif(companyFiling == "10-Q"):
            continue
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter10q += 1
            logger.info(f"Processing 10Q for : {companyName}\n")
            filingFile = sec_Api.get10QFilingForCompanyApi(splitLineCompanyInfo)
            print(filingFile.content)
            time.sleep(1/10)
            helper.process_10q(filingFile, sec_Api, companyInfoTuple)
        
        elif(companyFiling == "8-K"):
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
        
        elif(companyFiling == "11-K"):
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 11-K for : {companyName}\n")
            filingFile = sec_Api.get8KFilingForCompanyApi(splitLineCompanyInfo)
            print(f"filing file: {filingFile}")
            #time.sleep(3)
            helper.process_11k(filingFile, sec_Api, companyInfoTuple)
            fileCounter11k+=1
            pass


logger.info("Processed " + str(fileCounter13fhr) + " 13F-HR files in master file.")
logger.info("Processed " + str(fileCounter10k) + " 10k files in master file.")
logger.info("Processed " + str(fileCounter10q) + " 10q files in master file.")
logger.info("Processed " + str(fileCounter8k) + " 8k files in master file.")