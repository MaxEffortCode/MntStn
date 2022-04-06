import re
import os
import xml.etree.ElementTree as ET
import pandas as pd

from IPython.display import display

from bs4 import BeautifulSoup
from Settings.setup_logger import logging

import sys

logger = logging.getLogger(__name__)

class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        edgarIndexFileDownloadPath = f"{os.path.dirname(__file__)}\\resources\edgar-full-index-archives\master-{year}-QTR{qtr}.txt"
        logger.info(f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:  
                logger.info("Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))

        return edgarIndexFileDownloadPath

    def process_13f_hr_subtree(self, subtree, out_file):
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
            childTag = child.tag[startIndex + 1: ]
            if ((child.text == None) and (isinstance(child.attrib, dict)) and (isinstance(child, ET.Element)) or (child.text.isspace())) :
                for nestedChild in child:
                    startIndex = nestedChild.tag.find('}')
                    nestedChildTag = nestedChild.tag[startIndex + 1: ]
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
        line = nameOfIssuer + ',' + cusip + ',' + value + ',' + shares + ',' + sshPrnamtType + ',' + putCall + ',' + investmentDiscretion + "," + otherManager + ',' + soleVotingAuthority + ',' + sharedVotingAuthority + ',' + noneVotingAuthority + "\n"
        out_file.write(line)

    def process_13f_hr(self, filingFile):

        pattern = b'<(.*?)informationTable\s|<informationTable'
        matchInformationTableStart = re.search(pattern, filingFile.content)

        pattern2 = b'</(\w*):informationTable>|</informationTable>.*?'
        match2InformationTableEnd = re.search(pattern2, filingFile.content)

        fileByteString = filingFile.content[matchInformationTableStart.start() : match2InformationTableEnd.end()]
        root = ET.fromstring(fileByteString.decode())

        with open("Apps/Collection/src/resources/13F-HR-parsed-data.csv", 'a') as out_file:
                for child in root:
                    self.process_13f_hr_subtree(child, out_file)

    def process_10k(filingFile, secApi):
        for file in filingFile.json()['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = secApi.baseUrl + filingFile.json()['directory']['name'] + "/" + file['name']
                logger.info(f"Searching through: {xmlSummary}")
                base_url = xmlSummary.replace('FilingSummary.xml', '')
                content = secApi.get(xmlSummary).content
                soup = BeautifulSoup(content, 'lxml')

                reports = soup.find('myreports')
                master_reports = []

                # loop through each report in the 'myreports' tag but avoid the last one as this will cause an error.
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
                    item1 = r"Consolidated Balance Sheets"
                    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
                    item3 = r"Consolidated Statements of Operations"
                    item4 = r"Consolidated Statements of Cash Flows"
                    item5 = r"Consolidated Statement of Changes in Stockholders' Equity and Changes in Net Assets"
                    item6 = r"Consolidated Statements of Stockholder's (Deficit) Equity"
                    report_list = [item1, item2, item3, item4, item5, item6]

                    if report_dict['name_short'] in report_list:
                        print('-'*100)
                        print(report_dict['name_short'])
                        print(report_dict['url'])
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
                            if (column != "12 Months Ended"):
                                properHeaders.append(column)
                    headersOfFinancialStatements.append(properHeaders)

                headersOfFinancialStatementsColumnLengths = []
                for index, headers in enumerate(headersOfFinancialStatements):
                    print(index, headers)
                    headersOfFinancialStatementsColumnLengths.append(len(headers))


                print("================== headersOfFinancialStatementsColumnLengths ===================== ")
                print((headersOfFinancialStatementsColumnLengths))

                dataOfFinancialStatements = []
                #for headerOfFinancialStatementColumnLength in headersOfFinancialStatementsColumnLengths:
                    #print("================== headerOfFinancialStatementColumnLength ===================== ")
                    #print(headerOfFinancialStatementColumnLength)
                for dataNestedList in allData:
                    properData = []
                    for data in dataNestedList:
                        if len(data) < len(headersOfFinancialStatementsColumnLengths):
                            break
                        else:
                            properData.append(data)
                    dataOfFinancialStatements.append(properData)

                #print("================== dataOfFinancialStatements ===================== ")
                #print((dataOfFinancialStatements))

                #print("================== dataOfFinancialStatements SIZE ===================== ")
                #print(len(dataOfFinancialStatements))

                #for test in dataOfFinancialStatements:
                #    print("\n==================TEST==============")
                #    print(test)

                # Put the data in a DataFrame
                
                for index, financialStatement in enumerate(dataOfFinancialStatements):
                    dataFrame = pd.DataFrame(financialStatement)

                    #print("================== dataFrame ===================== ")
                    #print(" ")
                    #print((dataFrame))

                    print("================== headersOfFinancialStatements[index][index] ===================== ")
                    print(headersOfFinancialStatements[index][index])

                    #Display
                    #print('-'*100)
                    #print('Before Reindexing')
                    #print('-'*100)
                    #print(f"{dataFrame.head()}")

                    # Define the Index column, rename it, and we need to make sure to drop the old column once we reindex.
                    dataFrame.index = dataFrame[0]
                    dataFrame.index.name = "Category"
                    dataFrame = dataFrame.drop(0, axis = 1)

                    # Display
                    #print('-'*100)
                    #print('Before Regex')
                    #print('-'*100)
                    #print(f"{dataFrame.head()}")

                    dataFrame = dataFrame.replace('[\$,)]','', regex=True )
                    dataFrame = dataFrame.replace('[(]','-', regex=True)
                    # income_df = income_df.replace('[]0-9[]', '', regex=True)
                    dataFrame = dataFrame.replace('', 'NaN', regex=True)
                    dataFrame = dataFrame.replace('[1]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[2]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[3]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[4]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[5]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[6]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[7]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[8]', 'NaN', regex=False)
                    dataFrame = dataFrame.replace('[9]', 'NaN', regex=False)
                    
                    # Display
                    #print('-'*100)
                    #print('Before type conversion')
                    #print('-'*100)
                    #print(f"{dataFrame.head()}")


                    dataFrame = dataFrame.loc[:, ~dataFrame.apply(lambda x: x.nunique() == 1 and x[0]=='NaN', axis=0)]
                    print(" ================== testyyy ===================== ")
                    print(dataFrame)

                    # everything is a string, so let's convert all the data to a float.
                    dataFrame = dataFrame.astype(float)

                    #print("")
                    #print(" ================== dataFrame after converting to float ===================== ")
                    #print("")
                    #print(dataFrame)

                    #print("")
                    print(" ================== header ===================== ")
                    #print("")
                    print(headersOfFinancialStatements[index])

                    #print("")
                    #print(" ================== dataFrame.columns ===================== ")
                    #print("")
                    #print(dataFrame.columns)
                    
                    # Change the column headers
                    #dataFrame.columns = header

                    # Display
                    #print('-'*100)
                    print('Final Product')
                    #print('-'*100)

                    # show the dataframe
                    display(dataFrame)

                    dataFrame.to_csv('Apps/Collection/src/resources/test-income-state.csv')

                    print('=====================sys path ===================')
                    print(sys.path)

                    dataFrame = dataFrame.index.names(headersOfFinancialStatements[index])

                    # drop the data in a CSV file if need be.
                    dataFrame.to_csv('Apps/Collection/src/resources/test-income-state.csv')


                
                

                    