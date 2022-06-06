from Apps.Collection.src.helper import *
from Apps.Collection.src.helper import helper
from Apps.Collection.src.api.sec_api import SecAPI
import itertools
from os.path import exists


def generate_companyInfoTuple(filing_type):
    sec_Api = SecAPI()
    yr = '2022'
    qtr = '1'

    response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
    # creates giant list with ALL company filing from the qrt
    edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
    
    # "/home/max/MntStn/Apps/Collection/src/resources/edgar-full-index-archives/master-2022-QTR1-test.txt"
    with open(edgarIndexFilePath) as file:
        for line in itertools.islice(file, 11, None):
            # 914208|Invesco Ltd.|3|2022-02-10|edgar/data/914208/0001209191-22-008399.txt
            splitLineCompanyInfo = line.strip().split("|")
            filing_url = splitLineCompanyInfo[4]
            companyName = splitLineCompanyInfo[1].strip()
            companyName = companyName.replace(',', '')
            companyName = companyName.replace(' ', '-')
            companyFiling = splitLineCompanyInfo[2]
            list_of_filing_tuples = []
            if companyFiling == filing_type:
                companyInfoTuple = (companyName, companyFiling, qtr, yr, filing_url)
                list_of_filing_tuples.append(companyInfoTuple)
    
    return list_of_filing_tuples
                
            
            
            

#this... this needs to be fixed
def test_download_htm_files():
    sec_Api = SecAPI()
    companyInfoTuplePlusUrl = generate_companyInfoTuple('497')
    filingFile = []
    for fileDir in companyInfoTuplePlusUrl:
        filingFile.append(fileDir[4])
    
    for filingDirUrl in filingFile:
        fileDirToTest = sec_Api.get497FilingForCompanyApi(companyInfoTuplePlusUrl)
        for file in fileDirToTest.json()['directory']['item']:
            file_url = sec_Api.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                        "/" + file['name']
            if '.htm' in file['name']:
                    download_htm_files(file, companyInfoTuplePlusUrl, file_url)
                    filing_type = companyInfoTuplePlusUrl[1].replace("/", "")
                    filing = companyInfoTuplePlusUrl[2].replace("/", "")
                    assert exists(f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuplePlusUrl[0]}/filings/\
                        {filing_type}/{companyInfoTuplePlusUrl[3]}/{filing}")
    
    assert(True)
            
    
def test_download_pdf_files():
    assert False

def test_pdf_dowload_from_url():
    assert False

def test_html_to_pdf():
    assert False

def test_downloadEdgarIndexFileAndGetPath():
    qtr = 1
    yr = 2021
    sec_Api = SecAPI()

    response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
    assert(response.status_code == 200)

    edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
    assert(type(edgarIndexFilePath) == str)

def test_process_13f_hr():
    assert False

def test_process_11k():
    assert False

def test_process_10k():
    assert False

def test_process_NT10k():
    assert False

def test_process_10KA():
    assert False

def test_process_10q():
    assert False

def test_process_8k():
    assert False

def test_process_4():
    assert False

def test_process_4A():
    assert False

def test_process_24F2NT():
    assert False

def test_process_497():
    assert False

def test_process_untracked():
    assert False