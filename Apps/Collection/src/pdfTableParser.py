import time
import os
import camelot
import pandas
import urllib.request
import re
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader 
from PyPDF2.errors import PdfReadError
from pdf2image import convert_from_path
from pyparsing import Regex
from Apps.Collection.src.data_base_helper import get_list_of_files



def htm_to_html(htm_link, file_path):
    urllib.request.urlretrieve(htm_link, file_path)

def read_html_pandas(request_content):
    list_of_terms = ['assets', 'net', 'income', 'Name:', 'Name: ', 'Name']
    pat1 = fr"\b({'|'.join(list_of_terms)})\b"

    # tables_on_page = pandas.read_html(request_content.text)
    # dummy = tables_on_page.apply(lambda x: x.str.findall(pat1, re.IGNORECASE).astype(bool)) \
    #       .any().astype(int).tolist()
    try:
        tables_on_page = pandas.read_html(request_content.text)
        for table in tables_on_page:
            print(f"table : {table} \n columns : {table.columns}")
    
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