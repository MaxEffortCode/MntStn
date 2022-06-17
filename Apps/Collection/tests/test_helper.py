from Apps.Collection.src.helper import *
from Apps.Collection.src.helper import helper
from Apps.Collection.src.api.sec_api import SecAPI
import itertools
import pandas as pd
from os.path import exists
from pathlib import Path
import shutil
import pytest

sec_api = SecAPI()

# I think that we should expand this later to do larger date range of forms
# We may learn that standardizations of forms change through out years
# and that in the future if they change, these tests will catch them and tell us
# Anything longer than this can take a while for certain forms.
years = ["2020"]
quarters = ["1"]

#
# Helper methods below for tests
# ================================================================================
# 
def get_quarterly_edgar_index_file_for_untracked_filing_form(edgar_index_file_path, qtr, yr):
    lines = []
    with open(edgar_index_file_path, "r") as file:
        for line in itertools.islice(file , 11, None): # TODO: make test later that all edgar master index files start reporting companies on this line
            lines.append(line)
    
    forms = ['13-F', '8-k', '13F-HR/A', '13F-HR', '10-K', '10-K/A', '10-Q', '10-Q/A']
    for form in forms:
        temp_form_name = form.replace("/", "")
        temp_form_name = temp_form_name.replace(',', '')
        temp_form_name = temp_form_name.replace(' ', '-')

    path = f"{os.path.dirname(__file__)}/resources/edgar-archives/{yr}/{qtr}"
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    new_path = f"{path}/all-companies-with-untracked-filings.csv"
    
    with open(new_path, "w+") as file:
        for line in lines:
            split_line_company_info = line.strip("\n").split("|")
            company_filing = split_line_company_info[2]
            if(company_filing not in form):
                file.write(line)
    file.close()
    return new_path
    

def get_quarterly_edgar_index_file_for_single_filing_form(form, edgar_index_file_path, qtr, yr):
    lines = []
    with open(edgar_index_file_path, "r") as file:
        for line in itertools.islice(file , 11, None): # TODO: make test later that all edgar master index files start reporting companies on this line
            lines.append(line)
            
    temp_form_name = form.replace("/", "")
    temp_form_name = temp_form_name.replace(',', '')
    temp_form_name = temp_form_name.replace(' ', '-')

    path = f"{os.path.dirname(__file__)}/resources/edgar-archives/{yr}/{qtr}"
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    new_path = f"{path}/all-companies-with-{temp_form_name}-filings.csv"

    with open(new_path, "w+") as file:
        for line in lines:
            split_line_company_info = line.strip("\n").split("|")
            company_filing = split_line_company_info[2]
            if(company_filing == form):
                file.write(line)
    file.close()
    return new_path

def get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form_name):
    quarterly_edgar_index_file_paths_for_single_filing_form_list = []
    
    if filing_form_name == "Untracked":
        for yr in years:
            for qtr in quarters:
                #TODO: make a collection of all the file types
                # not covered already in the tests (i.e. 13f, 8k,..)
                response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
                edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
                
        
    for yr in years:
        for qtr in quarters:
            response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
            edgar_index_file_path = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
            quarterly_form_path = get_quarterly_edgar_index_file_for_single_filing_form(filing_form_name, edgar_index_file_path, qtr, yr)
            quarterly_edgar_index_file_paths_for_single_filing_form_list.append(quarterly_form_path)
    return quarterly_edgar_index_file_paths_for_single_filing_form_list

def get_company_info_tuple(file_path_name, line):
    yr = file_path_name.split('/')[-3]
    qtr = file_path_name.split('/')[-2]
    split_line_company_info = line.strip("\n").split("|")
    company_name = split_line_company_info[1].strip()
    company_name = company_name.replace(',', '')
    company_name = company_name.replace(' ', '-')
    company_filing = split_line_company_info[2]

    company_info_tuple = (company_name, company_filing, qtr, yr, split_line_company_info)
    return company_info_tuple
               
#
# ================================================================================
#

# TODO: We should refactor our form generators to specify paths so that we can download to TEST folder
# Traditionally in java, src folder is not for testing data and this is structued similar
# Fixtures seem cool - pretty much Junit's version of setup/beforeEach annotation
@pytest.fixture(autouse=True)
def setup():
    parent_path = Path(f"{os.path.dirname(__file__)}").parent
    src_resources_path = f"{parent_path}/src/resources"

    current_path = Path(f"{os.path.dirname(__file__)}")
    test_resources_path = f"{current_path}/resources"

    if(os.path.exists(src_resources_path)):
        shutil.rmtree(src_resources_path)
    if(os.path.exists(test_resources_path)):
        shutil.rmtree(test_resources_path)

    yield

def test_download_edgar_index_file_and_get_path():
    qtr = "1"
    yr = "2022"
    response = sec_api.getMasterEdgarIndexFileByQtrAndYrApi(qtr, yr)
    assert(response.status_code == 200)
    edgarIndexFilePath = helper.downloadEdgarIndexFileAndGetPath(response, qtr, yr)
    assert(type(edgarIndexFilePath) == str)

def test_process_13f_hr():
    filing_form = "13F-HR"
    quarterly_13f_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_13f_file_path_list)) # Check that there is at least one form to test
    
    for quarterly_13f_form_path in quarterly_13f_file_path_list:
        with open(quarterly_13f_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_13f_form_path, line)

                print(company_info_tuple)

                response = sec_api.get_13f_hr_filing_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_path = helper().process_13f_hr(response, company_info_tuple)
                assert(os.path.exists(file_path))
                           
                df = pd.read_csv(file_path)
                columnNames = ['nameOfIssuer','cusip','value','shares','sshPrnamtType','putCall','investmentDiscretion','otherManager','soleVotingAuthority','sharedVotingAuthority','noneVotingAuthority']
                
                assert(df.shape[1] == 11) # Check data frame headers
                assert(set(columnNames).issubset(df.columns)) # Check data frame Column Names
                assert(len(df.columns) != 0) # Check not empty

def test_process_13f_hr_amendment():
    filing_form = "13F-HR/A"
    quarterly_13f_amendment_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_13f_amendment_file_path_list)) # Check that there is at least one form to test
    
    for quarterly_13f_amendment_form_path in quarterly_13f_amendment_file_path_list:
        with open(quarterly_13f_amendment_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_13f_amendment_form_path, line)

                response = sec_api.get_13f_hr_filing_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_path = helper().process_13f_hr(response, company_info_tuple)
                assert(os.path.exists(file_path))
                           
                df = pd.read_csv(file_path)
                columnNames = ['nameOfIssuer','cusip','value','shares','sshPrnamtType','putCall','investmentDiscretion','otherManager','soleVotingAuthority','sharedVotingAuthority','noneVotingAuthority']
                
                assert(df.shape[1] == 11) # Check data frame headers
                assert(set(columnNames).issubset(df.columns)) # Check data frame Column Names
                assert(len(df.columns) != 0) # Check not empty

def test_process_10k():
    filing_form = "10-K"
    quarterly_10k_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_10k_file_path_list)) # Check that there is at least one form to test

    for quarterly_10k_form_path in quarterly_10k_file_path_list:
        with open(quarterly_10k_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_10k_form_path, line)

                response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_paths = helper.process_10k(response, sec_api, company_info_tuple)
                for path in file_paths:
                    assert(os.path.exists(path)) # Check file exists
                    df = pd.read_csv(path)
                    assert(len(df.columns) != 0) # Check not empty

def test_process_10k_amendment():
    filing_form = "10-K/A"
    quarterly_10k_amendment_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_10k_amendment_file_path_list)) # Check that there is at least one form to test

    for quarterly_10k_amendment_form_path in quarterly_10k_amendment_file_path_list:
        with open(quarterly_10k_amendment_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_10k_amendment_form_path, line)

                response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_paths = helper.process_10k(response, sec_api, company_info_tuple)
                for path in file_paths:
                    assert(os.path.exists(path)) # Check file exists
                    df = pd.read_csv(path)
                    assert(len(df.columns) != 0) # Check not empty

def test_process_10q():
    filing_form = "10-Q"
    quarterly_10q_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_10q_file_path_list)) # Check that there is at least one form to test

    for quarterly_10q_form_path in quarterly_10q_file_path_list:
        with open(quarterly_10q_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_10q_form_path, line)

                response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_paths = helper.process_10q(response, sec_api, company_info_tuple)
                for path in file_paths:
                    assert(os.path.exists(path)) # Check file exists
                    df = pd.read_csv(path)
                    assert(len(df.columns) != 0) # Check not empty

def test_process_10q_amendment():
    filing_form = "10-Q/A"
    quarterly_10q_amendment_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_10q_amendment_file_path_list)) # Check that there is at least one form to test

    for quarterly_10q_amendment_form_path in quarterly_10q_amendment_file_path_list:
        with open(quarterly_10q_amendment_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_10q_amendment_form_path, line)

                response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)

                file_paths = helper.process_10q(response, sec_api, company_info_tuple)
                for path in file_paths:
                    assert(os.path.exists(path)) # Check file exists
                    df = pd.read_csv(path)
                    assert(len(df.columns) != 0) # Check not empty


def test_html_to_pdf():
    assert False

def test_process_11k():
    assert False

def test_process_NT10k():
    assert False

def test_process_10KA():
    assert False

def test_process_8k():
    filing_form = "8-K"
    quarterly_8k_file_path_list = get_range_of_quarterly_edgar_index_file_forms_for_single_filing_form(filing_form)
    assert(len(quarterly_8k_file_path_list)) # Check that there is at least one form to test

    for quarterly_8k_form_path in quarterly_8k_file_path_list:
        with open(quarterly_8k_form_path) as file:
            for line in itertools.islice(file, 0, None):
                company_info_tuple = get_company_info_tuple(quarterly_8k_form_path, line)
                
                response = sec_api.get_index_json_filing_response_for_company_api(company_info_tuple[4])
                assert(response.status_code == 200)
                time.sleep(1/10)
                
                file_paths = helper.process_8k(response, sec_api, company_info_tuple)
                for path in file_paths:
                    assert(os.path.exists(path)) # Check directory exists

def test_process_4():
    assert False

def test_process_4A():
    assert False

def test_process_24F2NT():
    assert False

def test_process_497():
    assert False

def test_download_pdf_files():
    assert False

def test_pdf_dowload_from_url():
    assert False


#this... this needs to be fixed
def test_download_htm_files():
    pass
    # companyInfoTuplePlusUrl = get_company_info_tuple_by_filing_type('497')
    # filingFile = []
    # for fileDir in companyInfoTuplePlusUrl:
    #     filingFile.append(fileDir[4])
    
    # for filingDirUrl in filingFile:
    #     fileDirToTest = sec_api.get497FilingForCompanyApi(companyInfoTuplePlusUrl)
    #     for file in fileDirToTest.json()['directory']['item']:
    #         file_url = sec_api.baseUrl + \
    #                     filingFile.json()['directory']['name'] + \
    #                     "/" + file['name']
    #         if '.htm' in file['name']:
    #                 download_htm_files(file, companyInfoTuplePlusUrl, file_url)
    #                 filing_type = companyInfoTuplePlusUrl[1].replace("/", "")
    #                 filing = companyInfoTuplePlusUrl[2].replace("/", "")
    #                 assert exists(f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuplePlusUrl[0]}/filings/\
    #                     {filing_type}/{companyInfoTuplePlusUrl[3]}/{filing}")
    
    # assert(True)

def untracked_files():
    filing_form = "Untracked"
    quarterly_untracked_file_path_list = get_quarterly_edgar_index_file_for_untracked_filing_form(filing_form)
    assert(len(quarterly_untracked_file_path_list))
    #TODO: to be continued 
    pass