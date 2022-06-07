import csv
from distutils.log import debug
from fileinput import filename
import re
import os
from shutil import ExecError
import time
import xml.etree.ElementTree as ET
from click import secho
import pandas as pd
import weasyprint
from Apps.Collection.src.pdfTableParser import htm_to_html, read_html_pandas

from Apps.Collection.src.api.sec_api import SecAPI
from IPython.display import display
from bs4 import BeautifulSoup, Doctype
from Settings.setup_logger import logging
from pathlib import Path
from urllib.request import urlretrieve, build_opener, install_opener


logger = logging.getLogger(__name__)


def download_htm_files(file, companyInfoTuple, file_url):
    try:
        if '.htm' in file['name']:
            filing_type = companyInfoTuple[1].replace("/", "")
            filing = companyInfoTuple[2].replace("/", "")
            path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/\
                {filing_type}/{companyInfoTuple[3]}/{filing}"
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            html_to_pdf(file_url, p, f"{filing_type}_filling")
            time.sleep(1/10)
        
        else:
            return
    
    except Exception as e:
            print(f"failed on {file_url}\n\
                with error: {e}")
            time.sleep(10)
    pass

def download_pdf_files(file, companyInfoTuple, file_url):
    try:
        
        if '.pdf' in file['name']:
            filing_type = companyInfoTuple[1].replace("/", "")
            filing = companyInfoTuple[2].replace("/", "")
            path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/\
                {filing_type}/{companyInfoTuple[3]}/{filing}"
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            pdf_dowload_from_url(file_url, p, f"{filing_type}_filling")
            time.sleep(1/10)
        
        else:
            return

    except Exception as e:
        print(f"failed on {file_url}\n\
            with error: {e}")
        time.sleep(10)

def pdf_dowload_from_url(url, path, pdf_name):
    sec_pdf = SecAPI()
    the_damn_pdf = sec_pdf.get(url)
    with open(f'{path}/{pdf_name}.pdf', 'wb') as fd:
        for chunk in the_damn_pdf.iter_content(2048):
            fd.write(chunk)

def html_save(file, companyInfoTuple, file_url):
    secApi = SecAPI()
    html_file = secApi.get(file_url)
    
    filing_type = companyInfoTuple[1].replace("/", "")
    filing = companyInfoTuple[2].replace("/", "")
    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/\
        {filing_type}/{companyInfoTuple[3]}/{filing}"
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    
    html_name = f"{filing_type}_filling"
    open(f'{p}/{html_name}_direct_save.html', 'wb').write(html_file.content)
    print(f"\n\n *******************  {p}/{html_name}_direct_save.pdf'  ********************* \n\n")
    time.sleep(100)



def html_to_pdf(url, path, pdf_name):
    pdf = weasyprint.HTML(url).write_pdf()
    open(f'{path}/{pdf_name}.pdf', 'ab').write(pdf)


class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        edgarIndexFileDownloadPath = f"{os.path.dirname(__file__)}\\resources\edgar-full-index-archives\master-{year}-QTR{qtr}.txt"
        logger.info(
            f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:
                logger.info(
                    "Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))

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
        line = [nameOfIssuer, cusip, value, shares, sshPrnamtType, putCall, investmentDiscretion,
            otherManager, soleVotingAuthority, sharedVotingAuthority, noneVotingAuthority]
        writer.writerow(line)

    def process_13f_hr(self, filingFile, companyInfoTuple):

        pattern = b'<(.*?)informationTable\s|<informationTable'
        matchInformationTableStart = re.search(pattern, filingFile.content)

        pattern2 = b'</(\w*):informationTable>|</informationTable>.*?'
        match2InformationTableEnd = re.search(pattern2, filingFile.content)

        fileByteString = filingFile.content[matchInformationTableStart.start(
        ): match2InformationTableEnd.end()]
        root = ET.fromstring(fileByteString.decode())

        headerLine = ["nameOfIssuer", "cusip", "value", "shares", "sshPrnamtType", "putCall", "investmentDiscretion",
            "otherManager", "soleVotingAuthority", "sharedVotingAuthority", "noneVotingAuthority"]

        path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/13f-hr-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)

        newPath = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/13f-hr-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}/13f-hr-data.csv"

        with open(newPath, 'w',  newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(headerLine)
                for child in root:
                    self.process_13f_hr_subtree(child, writer)

    # TODO make clean
    def process_11k(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            # file in  {'last-modified': '2022-01-13 07:31:12', 'name': '0000950170-22-000296-index-headers.html', 'type': 'text.gif', 'size': ''}
            name = file['name']
            print(f"name = {name}")

            if "11-k" not in name and "11k" not in name:
                continue

            end_bit_of_url = name
            xmlSummary = secApi.baseUrl + \
                filingFile.json()['directory']['name'] + "/" + file['name']
            logger.info(f"Searching through: {xmlSummary}")
            base_url = xmlSummary.replace(name, '')
            content = secApi.get(xmlSummary).content

            # print(content)
            soup = BeautifulSoup(content, 'lxml')
            print(f"\n\n\nsoup \n\n {soup.find_all('a')}")
            for table in soup.find_all('table'):
                for table_row in table:
                    print(f"\ntable row \n {table_row.text}\n")

            # main_url = base_url + end_bit_of_url
            # logger.info(f"Preforming GET on {main_url}")

            # content = secApi.get(main_url).content
            # soup = BeautifulSoup(content, 'xml')

            time.sleep(10)

    def process_10k(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
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
                    item1 = r"Consolidated Balance Sheets"
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
                    item3 = r"Consolidated Statements of Operations"
                    item4 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets"
                    item5 = r"Consolidated Statements of Stockholder's (Deficit) Equity"
                    report_list = [item1, item2, item3, item4, item5]

                    if report_dict['name_short'] in report_list:
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
                            hed_row = [ele.text.strip()
                                                      for ele in row.find_all('th')]
                            logger.info(
                                "\n================= statement_data INFORMATION =========\n")
                            logger.info(f"statement_data")
                            statement_data['headers'].append(hed_row)

                        else:
                            logger.info(
                                "Parsed an html file with a case we haven't handled yet.")

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
                    headersOfFinancialStatementsColumnLengths.append(
                        len(headers))
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
                        logger.info(
                            f"Financial statement is empty.\nIgnoring and continuing on.\n")
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

                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/10-k-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)

                    dataFrame.to_csv(
                        f"{path}/{reportListName}.csv", index=True, header=True)

    def process_NT10k(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            if 'nt' in file['name']:
                filing_type = companyInfoTuple[1].replace(" ", "")
                file_url = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
                path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{filing_type}/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                p = Path(path)
                p.mkdir(parents=True, exist_ok=True)
                html_to_pdf(file_url, p, f"{filing_type}_filling")
        return None

    def process_10KA(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            try:
                if '.htm' in file['name']:
                    filing_type = companyInfoTuple[1].replace("/", "")
                    filing = companyInfoTuple[2].replace("/", "")
                    file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                                        "/" + file['name']
                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{filing_type}/{companyInfoTuple[3]}/{filing}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)
                    html_to_pdf(file_url, p, f"{filing_type}_filling")
                    time.sleep(1/10)

                if '.pdf' in file['name']:
                    filing_type = companyInfoTuple[1].replace("/", "")
                    filing = companyInfoTuple[2].replace("/", "")
                    file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                                        "/" + file['name']
                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{filing_type}/{companyInfoTuple[3]}/{filing}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)
                    pdf_dowload_from_url(file_url, p, f"{filing_type}_filling")
                    time.sleep(1/10)

                else:
                    print(f"didnt attempt to download: {file['name']}\n \
                        at url: {file_url}")
                    time.sleep(1/10)
            except Exception as e:
                print(f"failed on {file_url}\n\
                    with error: {e}")
                time.sleep(10)
        return None

    def process_10q(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            # {'last-modified': '2022-02-09 09:00:46', 'name': 'FilingSummary.xml', 'type': 'text.gif', 'size': '34225'}
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
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
                    # [{'name_short': 'Document and Entity Information', 'name_long': '100000 - Document - Document and Entity Information',
                    # 'position': '1', 'category': 'Cover', 'url': 'https://www.sec.gov/Archives/edgar/data/1000045/000095017022000940/R1.htm'}]

                statements_url = []

                for report_dict in master_reports:
                    # short name html header
                    item1 = r"Consolidated Balance Sheets"
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
                    item3 = r"Consolidated Statements of Operations"
                    item4 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets"
                    item5 = r"Consolidated Statements of Stockholder's (Deficit) Equity"
                    report_list = [item1, item2, item3, item4, item5]

                    if report_dict['name_short'] in report_list:
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
                            hed_row = [ele.text.strip()
                                                      for ele in row.find_all('th')]
                            logger.info(
                                "\n================= statement_data INFORMATION =========\n")
                            logger.info(f"statement_data")
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
                    headersOfFinancialStatementsColumnLengths.append(
                        len(headers))
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
                        logger.info(
                            f"Financial statement is empty.\nIgnoring and continuing on.\n")
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

                    path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/10-q-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)

                    dataFrame.to_csv(
                        f"{path}/{reportListName}.csv", index=True, header=True)

    def process_8k(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            # file in  {'last-modified': '2022-01-13 07:31:12', 'name': '0000950170-22-000296-index-headers.html', 'type': 'text.gif', 'size': ''}
            name = file['name']
            if ".htm" in name and ".html" not in name:
                htm = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
                path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/8-k-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                end_bit_of_url = "8-k-filing.html"
                print(f"htm = {htm}")
                request_content = secApi.get(htm)
                read_html_pandas(request_content, companyInfoTuple)

            if(name != 'FilingSummary.xml'):
                continue

            xmlSummary = secApi.baseUrl + \
                filingFile.json()['directory']['name'] + "/" + file['name']
            logger.info(f"Searching through: {xmlSummary}")
            base_url = xmlSummary.replace('FilingSummary.xml', '')
            content = secApi.get(xmlSummary).content
            soup = BeautifulSoup(content, 'xml')

            end_bit_of_url = soup.find(doctype='8-K').contents[0]

            main_url = base_url + end_bit_of_url
            logger.info(f"Preforming GET on {main_url}")

            content = secApi.get(main_url).content
            soup = BeautifulSoup(content, 'xml')

            pdf = weasyprint.HTML(main_url).write_pdf()

            path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/8-k-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            try:
                # /home/max/MntStn/Apps/Collection/src/resources/companies

                open(f'{path}/{end_bit_of_url.strip(".htm")}.pdf', 'ab').write(pdf)

                for link in soup.find_all('a'):
                    attached_url = base_url + link.get('href')
                    pdf = weasyprint.HTML(attached_url).write_pdf()
                    open(f'{path}/{end_bit_of_url.strip(".htm")}.pdf',
                         'ab').write(pdf)

            except TypeError:
                logger.error(
                    f"Failed to concatenate str probs cause its <nonetype> \n")
                time.sleep(1)

            except:
                logger.error(f"http 404 not found \n")
                time.sleep(1)

        return

    def process_4(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            print(f"\n******** file json: {file} *********\n")
            if 'headers' in file['name']:
                base_link = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/"
                link = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
            else:
                continue

            content = secApi.get(link).content
            soup = BeautifulSoup(content, features="lxml")
            href_links = []
            for href_link in soup.find_all('a'):
                print(f"href : {href_link.contents[0]}")
                if 'html' in href_link.contents[0]:
                    href_links.append(href_link['href'])

            print(f"\n********links: {href_links} *********\n")

            for doc_link in href_links:
                path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{companyInfoTuple[1]}/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                p = Path(path)
                p.mkdir(parents=True, exist_ok=True)
                print(f"**** link: {base_link}/{doc_link} ****")
                html_to_pdf(f"{base_link}/{doc_link}", p, "doc4")

        return None

    def process_4A(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            print(f"\n******** file json: {file} *********\n")
            if 'headers' in file['name']:
                base_link = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/"
                link = secApi.baseUrl + \
                    filingFile.json()['directory']['name'] + "/" + file['name']
            else:
                continue

            content = secApi.get(link).content
            soup = BeautifulSoup(content, features="lxml")
            href_links = []
            for href_link in soup.find_all('a'):
                print(f"href : {href_link.contents[0]}")
                if 'html' in href_link.contents[0]:
                    href_links.append(href_link['href'])

            print(f"\n********links: {href_links} *********\n")

            for doc_link in href_links:
                path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{companyInfoTuple[1]}/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                p = Path(path)
                p.mkdir(parents=True, exist_ok=True)
                print(f"**** link: {base_link}/{doc_link} ****")
                html_to_pdf(f"{base_link}/{doc_link}", p, "doc4")
        return None

    def process_24F2NT(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                        "/" + file['name']
            try:
                if '.pdf' in file['name']:
                    download_pdf_files(file, companyInfoTuple, file_url)
                
                elif '.htm' in file['name']:
                    download_htm_files(file, companyInfoTuple, file_url)

                else:
                    print(f"didnt attempt to download: {file['name']}\n \
                        at url: {file_url}")
                    time.sleep(1/10)
                
            except Exception as e:
                print(f"failed on {file_url}\n\
                    with error: {e}")
                time.sleep(10)   
    
    def process_497(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                        "/" + file['name']
            try:
                if '.pdf' in file['name']:
                    download_pdf_files(file, companyInfoTuple, file_url)
                    html_save(file, companyInfoTuple, file_url)
                
                elif '.htm' in file['name']:
                    download_htm_files(file, companyInfoTuple, file_url)
                    html_save(file, companyInfoTuple, file_url)

                else:
                    print(f"didnt attempt to download: {file['name']}\n \
                        at url: {file_url}")
                    time.sleep(1/10)
                
            except Exception as e:
                print(f"failed on {file_url}\n\
                    with error: {e}")
                time.sleep(10)
                
    def process_untracked(filingFile, secApi, companyInfoTuple):
        for file in filingFile.json()['directory']['item']:
            file_url = secApi.baseUrl + \
                        filingFile.json()['directory']['name'] + \
                        "/" + file['name']
            try:
                if '.pdf' in file['name']:
                    download_pdf_files(file, companyInfoTuple, file_url)
                    html_save(file, companyInfoTuple, file_url)
                
                elif '.htm' in file['name']:
                    download_htm_files(file, companyInfoTuple, file_url)
                    html_save(file, companyInfoTuple, file_url)

                else:
                    print(f"didnt attempt to download: {file['name']}\n \
                        at url: {file_url}")
                    time.sleep(1/10)
                
            except Exception as e:
                print(f"failed on {file_url}\n\
                    with error: {e}")
                time.sleep(10)