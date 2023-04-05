import time
import os
import camelot
import pandas
import urllib.request
from asyncio.log import logger
from numpy import NaN
from pathlib import Path
from PyPDF2 import PdfFileWriter, PdfFileReader 
from PyPDF2.errors import PdfReadError
from pdf2image import convert_from_path


def get_list_of_files(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_list_of_files(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles


def count_files_in_dir(dir):
    count = 0
    dir_path = dir
    for path in os.scandir(dir_path):
        if path.is_file():
            count += 1
    return count

def htm_to_html(htm_link, file_path):
    urllib.request.urlretrieve(htm_link, file_path)

def read_html_pandas(request_content, companyInfoTuple):
    list_of_terms = ['assets', 'net', 'income', 'Net Revenues', 'Operating Loss', 'Net Income (Loss)', 'Net Income (Loss) per Share', 'Operating Income (Loss)',\
        'Revenues:', 'Total Revenues', 'Costs and Expenses:', 'Lease operating expenses', 'Income tax benefit (expense)', 'Net Income (Loss) from Continuing Operations',\
            'Income tax benefit (expense)', 'Lease operating expenses', 'Common stock repurchased for tax withholding', 'Tax effect of adjustments', 'Revenues',\
                'Costs and expenses', 'EBITDA', 'Propane', 'Capital expenditures:', '$']
    terms_indicating_thousands = ['thousands', 'THOUSANDS', 'Thousands', 'thousands:']
    is_in_thousands = False

    try:
        tables_on_page = pandas.read_html(request_content.text)

        for table in tables_on_page:
            #presumable in thousands except for shares
            if any(term in request_content.text for term in terms_indicating_thousands):
                is_in_thousands = True
                print(f"is in thousands = True")
                
            else:
                is_in_thousands = False
                print(f"is in thousands = False")
                
            #print all tables containing any values inside list of terms
            if any(term in table.values for term in list_of_terms):
                table = table.replace('$', NaN)
                table = table.replace(')', NaN)
                table = table.replace('(', NaN)
                table = table.loc[:,~table.columns.duplicated()]
                table = table.dropna(axis=1, how='all')
                table = table.dropna(axis=0, how='all')
                
                print(f"columns : {table.columns} table: {table}\n\n")
                #companyName, companyFiling, qtr, yr
                path = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/{companyInfoTuple[1]}_tier_2_data/{companyInfoTuple[3]}/{companyInfoTuple[2]}"
                p = Path(path)
                p.mkdir(parents=True,exist_ok=True)
                try:
                    table_num = count_files_in_dir(path)
                    table.to_csv(path_or_buf=f"{path}/{table_num}")
                    print(f"{path}/{table_num}")
                    time.sleep(100)
                except:
                    logger.error(f"failed converting table to csv on {path}")
                    
    
    except ValueError as e: print(e)


def read_pdf_camelot(pdf_file):
    PDF_PATH = pdf_file
    PDF_PATH_TEST_FILE = "Testing/boeing.pdf"
    pdf_doc = PdfFileReader(open(PDF_PATH_TEST_FILE, "rb"))

    print("---------------PDF's info---------------")
    print(pdf_doc.documentInfo)
    print("PDF is encrypted: " + str(pdf_doc.isEncrypted))
    print("---------------Number of pages---------------")
    print(pdf_doc.numPages)

    dir_list = os.listdir(PDF_PATH)
    list_of_files = get_list_of_files(PDF_PATH)
    print(f"{list_of_files}")

    for file in list_of_files:
        name, extension = os.path.splitext(file)
        try:
            if extension == ".pdf":
                output_camelot = camelot.read_pdf(
                    filepath=file, pages='all', flavor="stream")
                
                for table in output_camelot:
                    table_shape = table.shape
                    # if function to weed out unessesary dataframes
                    if len(table_shape) < 2 or table_shape[0] < 4 or table_shape[1] < 4:
                        continue
                    
                    print(output_camelot) 
                    print(table.df)
                    head, tail = os.path.split(name)
                    table.df.to_csv(f"{head}/table_{table.page}")

                    print(f"succesed file at : {head}/table_{table.page}")
                    print(table.parsing_report)
        
        except IndexError as e: print(f"Failed on file {file},\n {e}")
        
        except ValueError  as e: print(e)
        
        except PdfReadError as e: print(e)

if __name__ == "__main__":
    #read_pdf_camelot("/home/max/MntStn/Apps/Collection/src/resources/companies/")
    file_path = "/home/max/MntStn/Apps/Collection/src/resources/companies/Vivos-Therapeutics-Inc./filings/8-k-filing/2022/test.html"
    
    htm_to_html("https://www.sec.gov/Archives/edgar/data/1000230/000143774922007553/occ20220329_8k.htm", file_path)
    
    read_html_pandas(file_path)