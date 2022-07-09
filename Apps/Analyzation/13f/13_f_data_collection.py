from tickers import get_source
import matplotlib.pyplot as plt
import os
import csv
import time
import pandas

tracked_companies = []

def get_ticker(company_name):
    soup = get_source(company_name)
    print(soup)

def clean_company_name(company_name):
    company_name = company_name.upper()
    company_name = company_name.replace(" ", "")
    company_name = company_name.replace(".", "")
    company_name = company_name.replace(",", "")
    company_name = company_name.replace("-", "")
    company_name = company_name.replace("&", "AND")
    company_name = company_name.replace("(", "")
    company_name = company_name.replace(")", "")
    company_name = company_name.replace("CORPORATION", "CORP")
    
    return company_name


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


def create_full_qtr_list_of_13f(file_arr):
    with open('13f_collection.csv', 'a', newline='') as csv_header:
        csv_writer = csv.writer(csv_header, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['nameOfIssuer', 'cusip', 'sshPrnamtType', 'putCall', 'investmentDiscretion',\
            'otherManager', 'soleVotingAuthority', \
            'sharedVotingAuthority','noneVotingAuthority'])
        
    
    for file in file_arr:
        try:
            with open(file, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(csv_reader)
                for row in csv_reader:
                    try:
                       with open('13f_collection.csv', 'a', newline='') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerow(row)
                    except ValueError as e:
                        continue
                        
        except(FileNotFoundError):
            continue
        
        except(IndexError):
            continue

    return '13f_collection.csv'

    

if __name__ == "__main__":
    #clear_csv('13f_collection.csv')
    #file_arr = collect_13_f_companies_and_shares()
    #file_13f = create_full_qtr_list_of_13f(file_arr)
    
    #    df['Total'] = df.groupby(['nameOfIssuer', 'cusip', 'sshPrnamtType', 'putCall', 'investmentDiscretion', 'otherManager', 'soleVotingAuthority', 'sharedVotingAuthority','noneVotingAuthority'])['value']['shares'].transform('sum')

    df = pandas.read_csv('13f_collection.csv', header=0, index_col='Cusip')
    df = df.groupby(['cusip'])

    with open('delete_me.txt', 'w', newline='') as txt_file:
        for key, item in df:
            txt_file.write(f"Key is: {(key)} \n head is : {df.head()}\n ")
            #txt_file.write(f"{(item)}, \n\n")

    #nameOfIssuer,cusip,value,shares,sshPrnamtType,putCall,investmentDiscretion,otherManager,soleVotingAuthority,sharedVotingAuthority,noneVotingAuthority

    #create_2D_graph('shares_bought.csv', x_label='Companies', y_label='Shares Bought', title='stocks from 2022 Q1', x_row=0, y_row=1)
