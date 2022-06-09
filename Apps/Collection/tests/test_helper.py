from Apps.Collection.src.helper import *
from Apps.Collection.src.helper import helper
from Apps.Collection.src.api.sec_api import SecAPI
import itertools
import pandas as pd
from os.path import exists

# I think that we should expand this later to do larger date range of forms
# We may learn that standardizations of forms change through out years
# and that in the future if they change, these tests will catch them and tell us

sec_Api = SecAPI()

years = ["2020", "2021"]
quarters = ["1", "2", "3", "4"]

response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)

#
# Helper methods below for tests
# ===================================================================
def get_company_info_tuple_by_filing_type(filing_type):
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

def get_quarterly_edgar_index_file_for_single_filing_form(form, edgarIndexFilePath, qtr, yr):
    with open(edgarIndexFilePath, "r") as file:
        for line in itertools.islice(file , 11, None): # TODO: find out if all edgar master index files start reporting companies on this line
            lines = file.readLines()
            
    edgarIndexFilePathForSingleForm = f"{os.path.dirname(__file__)}/resources/edgar-archives/{year}/{qtr}/{form.replace("/", "")}.txt"
    with open(edgarIndexFilePathForSingleForm, "w") as file:
        for line in lines:
            splitLineCompanyInfo = line.strip("\n").split("|")
            companyFiling = splitLineCompanyInfo[2]
            if(companyFiling == form):
                file.write(line)
    file.close()
    return edgarIndexFilePathForSingleForm

def get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filingFormName):
    quarterlyEdgarIndexFilePathsForSingleFilingFormList = []
    for yr in years:
    for qtr in quarters:
        response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
        edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
        quarterlyFormPath = get_quarterly_edgar_index_file_for_single_filing_form(filingFormName, edgarIndexFilePath, qtr, yr)
        quarterlyEdgarIndexFilePathsForSingleFilingFormList.append(quarterlyFormPath)
    return quarterlyEdgarIndexFilePathsForSingleFilingFormList

def get_company_info_tuple(filePathName, splitLineCompanyInfo):
    year = filePathName.split('/')[-3]
	qtr = filePathName.split('/')[-2]	
	splitLineCompanyInfo = companyInfoLine.strip("\n").split("|")
	companyName = splitLineCompanyInfo[1].strip()
	companyName = companyName.replace(',', '')
	companyName = companyName.replace(' ', '-')
	companyFiling = splitLineCompanyInfo[2]
	companyInfoTuple = (companyName, companyFiling, qtr, yr)
	return companyInfoTuple
                
# ===================================================================       

def test_download_edgar_index_file_and_get_path():
    qtr = "1"
    yr = "2022"
    response = sec_Api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
    assert(response.status_code == 200)
    edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
    assert(type(edgarIndexFilePath) == str)

def test_process_13f_hr():
    filingForm = "13F-HR"
    quarterly13fFilePathList = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filingForm)
    
    for quarterly13fFormPath in quarterly13fFilePathList:
        with open(quarterly13fFormPath) as file:
            splitLineCompanyInfo = line.strip("\n").split("|")
            companyInfoTuple = get_company_info_tuple(quarterly13fFormPath, splitLineCompanyInfo)
    
            filingFile = sec_Api.get13FHRFilingForCompanyApi(splitLineCompanyInfo)
            assert(response.status_code == 200)
            time.sleep(1/10)
            
            # When sec_form_crawler processes 13f and calls the below line of code
            # {os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/13f-hr-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}/13f-hr-data.csv"
            # {os.path.dirname(__file__)} resorts to MntStn/Apps/Collection/src/ ... 
            # I am hoping since helper() gets created within a diff directory, the dunder variable will instead create the file under
            # MntStn/Apps/Collection/tests so that we can test this file
            helper().process_13f_hr(filingFile, companyInfoTuple)
            file_path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/13f-hr-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}/13f-hr-data.csv"
            assert(os.path.exists(file_path))
            
            dataFrame = pd.read_csv(file_path)
            print("Data Frame")
            print(dataFrame)
            
            print("\n\nData Frame Total Columns")
            print(dataFrame.shape[1])
            
            print("\n\nData Frame Column Names")
            print(dataFrame.columns)
            
            print("\n\nData Frame Checking For Null Values")
            print(dataFrame.isna())
    
#this... this needs to be fixed
def test_download_htm_files():
    companyInfoTuplePlusUrl = get_company_info_tuple_by_filing_type('497')
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
