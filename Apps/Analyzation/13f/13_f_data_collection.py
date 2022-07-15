from email import header
from tickers import get_source
import matplotlib.pyplot as plt
import os
import csv
import re
import time
import pandas

tracked_companies = []

def get_ticker(company_name):
    soup = get_source(company_name)


def clear_csv(csv_file):
    file = open(csv_file, 'r+')
    file.truncate(0)
    file.close()

def create_2D_graph(csv_file_path, x_label, y_label, title, x_row = 0, y_row = 1):
    x = []
    y = []
    
    z = 0
    with open(csv_file_path,'r') as csvfile:
            
        
        plots = csv.reader(csvfile, delimiter = ',')
        
        for row in plots:
            x.append(row[x_row])
            y.append(int(row[y_row]))
            z+=1
            if z > 20:
                break
    
    plt.bar(x, y, color = 'g', width = 0.72, label = "Age")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.show()

def collect_13_f_companies_and_shares():
    path = f"/home/max/MntStn/Apps/Collection/src/resources/companies"
    subDir = [x for x in os.walk(path)]
    data_locations = []
    for sub in subDir:
        if '13F-HR-data.csv' in sub[2]:
            end_file = sub[2]
            end_file = str(end_file)
            end_file = end_file[2:-2]
            location = f"{sub[0]}/{end_file}"
            data_locations.append(location)
      
    return [sub for sub in data_locations]


def create_full_qtr_list_of_13f(file_arr, path):
    with open(path, 'a', newline='') as csv_header:
        csv_writer = csv.writer(csv_header, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['nameOfIssuer','cusip','value','shares','sshPrnamtType',\
            'putCall','investmentDiscretion','otherManager','soleVotingAuthority','sharedVotingAuthority','noneVotingAuthority'
            ])
        
    
    for file in file_arr:
        try:
            with open(file, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(csv_reader)
                for row in csv_reader:
                    row[1] = row[1].upper()
                    try:
                       with open(path, 'a', newline='') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerow(row)
                    except ValueError as e:
                        continue
                        
        except(FileNotFoundError):
            continue
        
        except(IndexError):
            continue

    return path

def read_all_copmany_names_from_edgar_master(edgar_path, save_path):
    with open(save_path, 'w', newline='') as csv_header:
        csv_writer = csv.writer(csv_header, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['nameOfIssuer','cusip','value','shares','sshPrnamtType',\
            'putCall','investmentDiscretion','otherManager','soleVotingAuthority','sharedVotingAuthority','noneVotingAuthority'
            ])
    
    with open(edgar_path, 'r', newline='') as edgar_file:
        with open(save_path, 'r+', newline='') as new_file:
            try:
                for x in range(12):
                    #ignore intro lines
                    next(edgar_file)
                
                last_row = None
                for row in edgar_file:
                    row_split = row.split("|")
                    try:
                        if row_split[1] == last_row:
                            continue

                        last_row = row_split[1]
                        
                        csv_writer = csv.writer(new_file, delimiter=',',
                            escapechar=' ', quoting=csv.QUOTE_NONE)
                        
                        company_name = re.sub('"', '', row_split[1])
                        company_name = re.sub(',', '', row_split[1])
                        cik = row_split[0]
                        csv_writer.writerow([cik, company_name])
                                
                    except ValueError as e:
                        continue
                            
            except(FileNotFoundError):
                return("file_not_found")
            
            except(IndexError):
                return("index error")

    return save_path


def match_company_names_to_cusip(collection_13f_file, save_file):
    df = pandas.read_csv(collection_13f_file, header=0)
    df = df.groupby(['cusip'])
    
    with open(save_file, 'w', newline='') as csv_header:
        headerList = ['CIK','nameOfIssuer','Ticker']
        csv_writer = csv.DictWriter(csv_header, delimiter=',', 
                        fieldnames=headerList)
        csv_writer.writeheader()
        
    with open(save_file, 'a+', newline='') as save_file:
        for key, item in df:
            csv_writer = csv.writer(save_file, delimiter=',',
                escapechar=' ', quoting=csv.QUOTE_NONE)
            ticker = get_source(key)
            csv_writer.writerow([key, item['nameOfIssuer'].iloc[0], ticker])
    
    return save_file

def merge_cik_to_cusip(collection_cusip, collection_cik, save_file):
    cusip_df = pandas.read_csv(collection_cusip, header=0, index_col=['cusip'])
    cik_df = pandas.read_csv(collection_cik, header=0, index_col=['nameOfIssuer'])
    with open(save_file, 'a+', newline='') as save_file:
        for key, item in cusip_df.iterrows():
            #print(f"key: {key} item: {item['nameOfIssuer']}\n\n")
            if item['nameOfIssuer'] in cik_df.index:
                print(f"{item['nameOfIssuer']}, {item['Ticker']}, {cik_df._get_value(item['nameOfIssuer'], 'CIK')}")

    #merged_df.to_csv(path_or_buf='merged_csv.csv')
    
    return save_file


if __name__ == "__main__":
    #company_ciks = read_all_copmany_names_from_edgar_master('Apps/Collection/src/resources/edgar-full-index-archives/master-2020-QTR1.txt', 
                                                            #'company_cusip_name_ticker_collection.csv')
    
    #clear_csv('13f_collection.csv')
    #file_arr = collect_13_f_companies_and_shares()
    #file_13f = create_full_qtr_list_of_13f(file_arr, '13f_collection.csv')
    cusip_colection = match_company_names_to_cusip('13f_collection.csv', 'company_cusip_name_ticker_collection.csv')
    merge_cik_to_cusip('company_cusip_name_ticker_collection.csv', 'cik_companyName.csv', 'merged.csv')
    

    #df = pandas.read_csv(file_13f, header=0)
    #print(list(df.columns))
    #df['Total'] = df.groupby(['nameOfIssuer', 'cusip', 'sshPrnamtType', 'putCall', 'investmentDiscretion', 'otherManager', 'soleVotingAuthority', 'sharedVotingAuthority','noneVotingAuthority'])['value']['shares'].transform('sum')

    #df = df.groupby(['cusip'])

#     with open('delete_me.txt', 'w', newline='') as txt_file:
#         for key, item in df:
#             ticker = get_ticker(key)
#             txt_file.write(f"Key is: {(key)} Ticker is: {ticker}\n")
            
#             txt_file.write(f"{(item)}, \n")
#             try:
#                 mean_val = item['shares'].sum() / item['value'].sum()
            
#             except ValueError as e:
#                 print(f"value fail:  {item['shares'].sum()} / {item['value'].sum()}")
                
#             txt_file.write(f"shares sum : {item['shares'].sum()}  mean price in Thousands?: {mean_val}\n\n")

    #nameOfIssuer,cusip,value,shares,sshPrnamtType,putCall,investmentDiscretion,otherManager,soleVotingAuthority,sharedVotingAuthority,noneVotingAuthority

    #create_2D_graph('shares_bought.csv', x_label='Companies', y_label='Shares Bought', title='stocks from 2022 Q1', x_row=0, y_row=1)
