import csv
import re
import os
import time
import xml.etree.ElementTree as ET
import pandas as pd
import pdfkit

from distutils.log import debug
from fileinput import filename
from Apps.Collection.src.pdfTableParser import htm_to_html, read_html_pandas
from Apps.Collection.src.api.sec_api import SecAPI
from bs4 import BeautifulSoup
from Settings.setup_logger import logging
from pathlib import Path
from urllib.request import urlretrieve, build_opener, install_opener

logger = logging.getLogger(__name__)



def download_pdf_by_url(url, full_path_and_file_name, sec_api):
    the_damn_pdf = sec_api.get(url)
    with open(f"{full_path_and_file_name}.pdf", "wb") as fd:
        for chunk in the_damn_pdf.iter_content(2048):
            fd.write(chunk)
    
    return f'{full_path_and_file_name}.pdf'

def html_save(file, companyInfoTuple, file_url):
    secApi = SecAPI()
    html_file = secApi.get(file_url)
    filing_type = companyInfoTuple[1].replace("/", "")
    filing = companyInfoTuple[2].replace("/", "")
    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{filing_type}/{companyInfoTuple[3]}/{filing}"
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    
    html_name = f"{filing_type}_filling"
    open(f'{p}/{html_name}_direct_save.html', 'wb').write(html_file.content)

    return f'{p}/{html_name}_direct_save.html'



def xlsx_to_csv(url, path):
    df = pd.read_excel(url, index_col=0)
    df.to_csv(path)

class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        path = f"{os.path.dirname(__file__)}/resources/edgar-full-index-archives"
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)

        edgarIndexFileDownloadPath = f"{path}/master-{year}-QTR{qtr}.txt"
        logger.info(f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:
                logger.info("Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))
        return edgarIndexFileDownloadPath

    def process_13f_hr_subtree(self, subtree, writer):
        nameOfIssuer = ''
        cusip = ''
        value = ''
        shares = ''
        sshPrnamtType = ''
        investmentDiscretion = ''
        putCall = ''
        otherManager = ''
        soleVotingAuthority = ''
        sharedVotingAuthority = ''
        noneVotingAuthority = ''

        for child in subtree:
            startIndex = child.tag.find('}')
            childTag = child.tag[startIndex + 1:]
            if ((child.text == None) and (isinstance(child.attrib, dict)) and (isinstance(child, ET.Element)) or (child.text.isspace())):
                for nestedChild in child:
                    startIndex = nestedChild.tag.find('}')
                    nestedChildTag = nestedChild.tag[startIndex + 1:]
                    match nestedChildTag:
                        case 'sshPrnamt':
                            shares = nestedChild.text
                        case 'sshPrnamtType':
                            sshPrnamtType = nestedChild.text
                        case 'Sole':
                            soleVotingAuthority = nestedChild.text
                        case 'Shared':
                            sharedVotingAuthority = nestedChild.text
                        case 'None':
                            noneVotingAuthority = nestedChild.text
            else:
                match childTag:
                    case 'nameOfIssuer':
                        nameOfIssuer = child.text
                    case 'cusip':
                        cusip = child.text
                    case 'value':
                        value = child.text
                    case 'investmentDiscretion':
                        investmentDiscretion = child.text
                    case 'putCall':
                        putCall = child.text
                    case 'otherManager':
                        otherManager = child.text

        nameOfIssuer = nameOfIssuer.replace(",", "")
        line = [nameOfIssuer, cusip, value, shares, sshPrnamtType, putCall, investmentDiscretion, otherManager, soleVotingAuthority, sharedVotingAuthority, noneVotingAuthority]
        writer.writerow(line)

    def process_13f_hr(self, filingFile, companyInfoTuple):
        pattern = b'<(.*?)informationTable\s|<informationTable'
        matchInformationTableStart = re.search(pattern, filingFile.content)

        pattern2 = b'</(\w*):informationTable>|</informationTable>.*?'
        match2InformationTableEnd = re.search(pattern2, filingFile.content)

        fileByteString = filingFile.content[matchInformationTableStart.start(): match2InformationTableEnd.end()]
        root = ET.fromstring(fileByteString.decode())

        headerLine = ["nameOfIssuer", "cusip", "value", "shares", "sshPrnamtType", "putCall", "investmentDiscretion", "otherManager", "soleVotingAuthority", "sharedVotingAuthority", "noneVotingAuthority"]

        company_filing = companyInfoTuple[1]
        company_filing = company_filing.replace('/', '-')

        path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{company_filing}-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)

        newPath = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{company_filing}-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}/{company_filing}-data.csv"

        with open(newPath, 'w',  newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(headerLine)
                for child in root:
                    self.process_13f_hr_subtree(child, writer)
        return newPath




    def process_10k(filingFile, secApi, companyInfoTuple):
        financialStatementList = []
        for file in filingFile.json()['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                logger.info(f"Searching through: {xmlSummary}")
                base_url = xmlSummary.replace('FilingSummary.xml', '')
                content = secApi.get(xmlSummary).content
                soup = BeautifulSoup(content, 'lxml')

                reports = soup.find('myreports')
                master_reports = []

                for report in reports.find_all('report')[:-1]:
                    report_dict = {}
                    report_dict['name_short'] = report.shortname.text
                    report_dict['name_long'] = report.longname.text
                    report_dict['position'] = report.position.text
                    report_dict['category'] = report.menucategory.text
                    report_dict['url'] = base_url + report.htmlfilename.text
                    master_reports.append(report_dict)

                statements_url = []
                for report_dict in master_reports:
                    # short name html header
                    item1 = r"Consolidated Balance Sheets".lower()
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)".lower()
                    item3 = r"Consolidated Statements of Operations".lower()
                    item4 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets".lower()
                    item5 = r"Consolidated Statements of Stockholder's (Deficit) Equity".lower()
                    report_list = [item1, item2, item3, item4, item5]

                    #Some filing summaries have ^ but in ALL CAPS... they really need to standardize
                    # Also TODO: Add more items above, there are many financial statements we can grab from a 10k 
                    if report_dict['name_short'].lower() in report_list:
                        statements_url.append(report_dict['url'])

                statements_data = []

                for statement in statements_url:
                    statement_data = {}
                    statement_data['headers'] = []
                    statement_data['sections'] = []
                    statement_data['data'] = []

                    content = secApi.get(statement).content
                    report_soup = BeautifulSoup(content, 'html.parser')

                    # find all the rows, figure out what type of row it is, parse the elements, and store in the statement file list.
                    for index, row in enumerate(report_soup.table.find_all('tr')):
                        cols = row.find_all('td')

                        if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0):
                            reg_row = [ele.text.strip() for ele in cols]
                            statement_data['data'].append(reg_row)

                        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
                            sec_row = cols[0].text.strip()
                            statement_data['sections'].append(sec_row)

                        elif (len(row.find_all('th')) != 0):
                            hed_row = [ele.text.strip() for ele in row.find_all('th')]
                            statement_data['headers'].append(hed_row)
                        else:
                            logger.info("Parsed an html file with a case we haven't handled yet.")

                    statements_data.append(statement_data)

                allHeaders = [obj['headers'] for obj in statements_data]
                allData = [obj['data'] for obj in statements_data]

                headersOfFinancialStatements = []
                for headerNestedList in allHeaders:
                    properHeaders = []
                    for headers in headerNestedList:
                        for column in headers:
                            if not (column == "12 Months Ended" or column == "9 Months ended" or column == "3 Months ended"):
                                properHeaders.append(column)
                    headersOfFinancialStatements.append(properHeaders)

                headersOfFinancialStatementsColumnLengths = []
                for index, headers in enumerate(headersOfFinancialStatements):
                    headersOfFinancialStatementsColumnLengths.append(len(headers))
                dataOfFinancialStatements = []

                for index, dataNestedList in enumerate(allData):
                    properData = []
                    for data in dataNestedList:
                        if len(data) < headersOfFinancialStatementsColumnLengths[index]:
                            break
                        else:
                            properData.append(data)
                    dataOfFinancialStatements.append(properData)

                for index, financialStatement in enumerate(dataOfFinancialStatements):
                    dataFrame = pd.DataFrame(financialStatement)
                    # Define the Index column, rename it, drop the old column after reindexing
                    # fail: raise KeyError(key) from err
                    try:
                        dataFrame.index = dataFrame[0]

                    except(KeyError):
                        logger.info(f"Financial statement is empty.\nIgnoring and continuing on.\n")
                        continue

                    dataFrame.index.name = headersOfFinancialStatements[index][0]
                    dataFrame = dataFrame.drop(0, axis=1)

                    dataFrame = dataFrame.replace('\[\d+\]', '', regex=True)
                    dataFrame = dataFrame.replace('[\$,)%]', '', regex=True)
                    dataFrame = dataFrame.replace('[(]', '-', regex=True)
                    dataFrame = dataFrame.replace('', 'NaN', regex=True)

                    dataFrame = dataFrame.loc[:, ~dataFrame.apply(lambda x: x.nunique() == 1 and x[0] == 'NaN', axis=0)]

                    keyList = dataFrame.columns.values.tolist()
                    dict = {}

                    for i, key in enumerate(keyList):
                        dict[key] = headersOfFinancialStatements[index][i + 1]

                    dataFrame.rename(columns=dict, inplace=True)

                    reportListName = headersOfFinancialStatements[index][0].strip()

                    reportListName = re.sub('[\$,)(-]', '', reportListName)
                    reportListName = reportListName.replace(r'/', '')
                    reportListName = reportListName.replace('\\', '')
                    reportListName = reportListName.replace(' ', '-')

                    company_filing = companyInfoTuple[1]
                    company_filing = company_filing.replace('/', '-')

                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{company_filing}-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)

                    dataFrame.to_csv(f"{path}/{reportListName}.csv", index=True, header=True)
                    financialStatementList.append(f"{path}/{reportListName}.csv")
        return financialStatementList


    def process_10q(filingFile, secApi, companyInfoTuple):
        financialStatementList = []
        for file in filingFile.json()['directory']['item']:
            # {'last-modified': '2022-02-09 09:00:46', 'name': 'FilingSummary.xml', 'type': 'text.gif', 'size': '34225'}
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                base_url = xmlSummary.replace('FilingSummary.xml', '')
                content = secApi.get(xmlSummary).content
                soup = BeautifulSoup(content, 'lxml')

                reports = soup.find('myreports')
                master_reports = []

                for report in reports.find_all('report')[:-1]:
                    report_dict = {}
                    report_dict['name_short'] = report.shortname.text
                    report_dict['name_long'] = report.longname.text
                    report_dict['position'] = report.position.text
                    report_dict['category'] = report.menucategory.text
                    report_dict['url'] = base_url + report.htmlfilename.text
                    master_reports.append(report_dict)
                    # [{'name_short': 'Document and Entity Information', 'name_long': '100000 - Document - Document and Entity Information',
                    # 'position': '1', 'category': 'Cover', 'url': 'https://www.sec.gov/Archives/edgar/data/1000045/000095017022000940/R1.htm'}]

                statements_url = []

                for report_dict in master_reports:
                    # short name html header
                    item1 = r"Consolidated Balance Sheets".lower()
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)".lower()
                    item3 = r"Consolidated Statements of Operations".lower()
                    item4 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets".lower()
                    item5 = r"Consolidated Statements of Stockholder's (Deficit) Equity".lower()
                    report_list = [item1, item2, item3, item4, item5]

                    if report_dict['name_short'].lower() in report_list:
                        statements_url.append(report_dict['url'])

                statements_data = []

                for statement in statements_url:
                    statement_data = {}
                    statement_data['headers'] = []
                    statement_data['sections'] = []
                    statement_data['data'] = []

                    content = secApi.get(statement).content
                    report_soup = BeautifulSoup(content, 'html.parser')
                    # find all the rows, figure out what type of row it is, parse the elements, and store in the statement file list.
                    for index, row in enumerate(report_soup.table.find_all('tr')):
                        cols = row.find_all('td')

                        if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0):
                            reg_row = [ele.text.strip() for ele in cols]
                            statement_data['data'].append(reg_row)

                        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
                            sec_row = cols[0].text.strip()
                            statement_data['sections'].append(sec_row)

                        elif (len(row.find_all('th')) != 0):
                            hed_row = [ele.text.strip() for ele in row.find_all('th')]
                            statement_data['headers'].append(hed_row)

                        else:
                            logger.info(
                                "Parsed an html file with a case we haven't handled yet.")

                    statements_data.append(statement_data)

                # [[['Consolidated Balance Sheets - USD ($) $ in Thousands', 'Dec. 31, 2021', 'Mar. 31, 2021']]]
                allHeaders = [obj['headers'] for obj in statements_data]
                allData = [obj['data'] for obj in statements_data]

                headersOfFinancialStatements = []

                for headerNestedList in allHeaders:
                    properHeaders = []
                    for headers in headerNestedList:
                        for column in headers:
                            if not (column == "12 Months Ended" or column == "9 Months ended" or column == "3 Months ended"):
                                properHeaders.append(column)
                    headersOfFinancialStatements.append(properHeaders)

                headersOfFinancialStatementsColumnLengths = []
                for index, headers in enumerate(headersOfFinancialStatements):
                    headersOfFinancialStatementsColumnLengths.append(len(headers))
                dataOfFinancialStatements = []

                for index, dataNestedList in enumerate(allData):
                    properData = []
                    for data in dataNestedList:
                        if len(data) < headersOfFinancialStatementsColumnLengths[index]:
                            break
                        else:
                            properData.append(data)
                    dataOfFinancialStatements.append(properData)

                for index, financialStatement in enumerate(dataOfFinancialStatements):
                    dataFrame = pd.DataFrame(financialStatement)
                    # Define the Index column, rename it, drop the old column after reindexing
                    # fail: raise KeyError(key) from err
                    try:
                        dataFrame.index = dataFrame[0]

                    except(KeyError):
                        logger.info(f"Financial statement is empty.\nIgnoring and continuing on.\n")
                        continue

                    dataFrame.index.name = headersOfFinancialStatements[index][0]
                    dataFrame = dataFrame.drop(0, axis=1)

                    dataFrame = dataFrame.replace('\[\d+\]', '', regex=True)
                    dataFrame = dataFrame.replace('[\$,)%]', '', regex=True)
                    dataFrame = dataFrame.replace('[(]', '-', regex=True)
                    dataFrame = dataFrame.replace('', 'NaN', regex=True)

                    dataFrame = dataFrame.loc[:, ~dataFrame.apply(
                        lambda x: x.nunique() == 1 and x[0] == 'NaN', axis=0)]

                    keyList = dataFrame.columns.values.tolist()
                    dict = {}

                    for i, key in enumerate(keyList):
                        dict[key] = headersOfFinancialStatements[index][i + 1]

                    dataFrame.rename(columns=dict, inplace=True)

                    reportListName = headersOfFinancialStatements[index][0].strip(
                    )

                    reportListName = re.sub('[\$,)(-]', '', reportListName)
                    reportListName = reportListName.replace(r'/', '')
                    reportListName = reportListName.replace('\\', '')
                    reportListName = reportListName.replace(' ', '-')

                    company_filing = companyInfoTuple[1]
                    company_filing = company_filing.replace('/', '-')

                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{company_filing}-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)

                    dataFrame.to_csv(f"{path}/{reportListName}.csv", index=True, header=True)
                    
                    financialStatementList.append(f"{path}/{reportListName}.csv")
                    
        return financialStatementList

    def process_8k(filingFile, sec_api, company_info_tuple):
        filesCreatedList = []
        for file in filingFile.json()['directory']['item']:
            file_url = sec_api.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']

            # Some company filings have a forward slash like amendments
            # Using a forward slash in path name will break and isn't allowed so change to -
            company_filing = company_info_tuple[1]
            company_filing = company_filing.replace('/', '-')
            
            file_path_extension = file['name']
            file_path_extension = file_path_extension.split('.')
            file_path_extension = file_path_extension[0]
            
            path = f"{os.path.dirname(__file__)}/resources/companies/{company_info_tuple[0]}/filings/{company_filing}-filing/{company_info_tuple[3]}/{company_info_tuple[2]}"
            p = Path(path)
            try:
                if '.pdf' in file['name']:
                    print("About to create PDF")
                    p.mkdir(parents=True, exist_ok=True)
                    file_path = download_pdf_by_url(file_url, f'{path}/{file_path_extension}', sec_api)
                    filesCreatedList.append(file_path)

                elif ('.htm' or '.html') in file['name']:
                    print(f"\nabout to turn htm or html into a PDF with url: {file_url}")
                    print(f'should be saved under - {path}/{file_path_extension}.pdf')
                    p.mkdir(parents=True, exist_ok=True)
                    pdfkit.from_url(file_url, output_path = f'{path}/{file_path_extension}.pdf')
                    filesCreatedList.append(f"{path}/{file_path_extension}.pdf")
                
                elif 'xlsx' in file['name']:
                    print("xlsx to CSV about to create")
                    p.mkdir(parents=True, exist_ok=True)
                    xlsx_to_csv(file_url, f"{path}/{file_path_extension}.csv")
                    filesCreatedList.append(f"{path}/{file_path_extension}.csv")
                
                else:
                    # xml, zip, css, xsd, jpg, js, txt, etc
                    logger.info(f"Didn't attempt to download: {file['name']}\n at url: {file_url}")                
            except Exception as e:
                logger.info(f"Caught exception on {file_url}\n with error: {e}")
        return filesCreatedList


                
    def process_untracked(filingFile, secApi, companyInfoTuple):
        filesCreatedList = []
        for file in filingFile.json()['directory']['item']:
            company_filing = companyInfoTuple[1]
            company_filing = company_filing.replace('/', '-')
            
            file_path_extension = file['name']
            file_path_extension = file_path_extension.split('.')
            file_path_extension = file_path_extension[0]
            
            file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + "/" + file['name']
            
            path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{company_filing}-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
            p = Path(path)
            try:
                file_name = file['name']
                file_name = file_name.lower()
                if '.pdf' in file_name:
                    print("About to create PDF")
                    p.mkdir(parents=True, exist_ok=True)
                    file_path = download_pdf_by_url(file_url, f'{path}/{file_path_extension}', secApi)
                    filesCreatedList.append(file_path)
                    
                elif ('.htm' or '.html') in file['name']:
                    print(f"\nabout to turn htm or html into a PDF with url: {file_url}")
                    print(f'should be saved under - {path}/{file_path_extension}.pdf')
                    p.mkdir(parents=True, exist_ok=True)
                    pdfkit.from_url(file_url, output_path = f'{path}/{file_path_extension}.pdf')
                    filesCreatedList.append(f"{path}/{file_path_extension}.pdf")
                
                elif 'xlsx' in file_name:
                    print("xlsx to CSV about to create")
                    p.mkdir(parents=True, exist_ok=True)
                    xlsx_to_csv(file_url, f"{path}/{file_path_extension}.csv")
                    filesCreatedList.append(f"{path}/{file_path_extension}.csv")
                
                else:
                    # xml, zip, css, xsd, jpg, js, txt, etc
                    logger.info(f"attempted to download as : {file['name']}\n at url: {file_url}")
                    path = html_save(file, companyInfoTuple, file_url)
                    logger.info(msg = f"Saved {file['name']} as '.html'\n at url: {file_url}")
                    filesCreatedList.append(f"{path}")
                    time.sleep(1/10)
                
            except Exception as e:
                print(f"failed on {file_url}\n\
                    with error: {e}")
                time.sleep(10)

        return filesCreatedList
