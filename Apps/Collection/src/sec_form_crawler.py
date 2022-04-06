import itertools
import time
from Apps.Collection.src.api.sec_api import SecAPI
from Apps.Collection.src.helper import helper
from Settings.setup_logger import logging

logger = logging.getLogger(__name__)
sec_Api = SecAPI()

#TODO: refactor
yr = '2022'
qtr = '1'

response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
fileCounter13fhr = 0
fileCounter10k = 0

with open(edgarIndexFilePath) as file:
    for line in itertools.islice(file, 11, None):
        splitLineCompanyInfo = line.strip().split("|")

        companyName = splitLineCompanyInfo[1].strip()
        companyName = companyName.replace(' ', '_')
        companyFiling = splitLineCompanyInfo[2]

        if(companyFiling == "13F-HR"):
            companyInfoTuple = (companyName, companyFiling, qtr, yr) 
            fileCounter13fhr += 1
            logger.info(f"Processing 13F-HR for : {companyName}\n")
            filingFile = sec_Api.get13FHRFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
            helper().process_13f_hr(filingFile)

        elif(companyFiling == "10-K"):
            companyInfoTuple = (companyName, companyFiling, qtr, yr)
            fileCounter10k += 1
            logger.info(f"Processing 10-K for : {companyName}\n")
            filingFile = sec_Api.get10kFilingForCompanyApi(splitLineCompanyInfo)
            time.sleep(1/10)
        
            helper.process_10k(filingFile, sec_Api, companyInfoTuple)

logger.info("Processed " + str(fileCounter13fhr) + " 13F-HR files in master file.")
logger.info("Processed " + str(fileCounter10k) + " 10k files in master file.")