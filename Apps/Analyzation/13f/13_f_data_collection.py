import pandas
from email import header

import matplotlib.pyplot as plt
import os
import csv
import re
import time
import requests
from asyncio.log import logger
import random
import sys


# please delete me later im part of tickers.py
def get_cik_ticker_to_csv_from_sec(save_file='cik_ticker.csv', url=f'https://www.sec.gov/include/ticker.txt'):
    url = f'https://www.sec.gov/include/ticker.txt'

    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    request_result = requests.get(url, headers=headers)
    logger.info(f"Getting cik_ticker list at {url}")

    open('cik_ticker.txt', 'wb').write(request_result.content)

    with open('cik_ticker.txt', 'r') as txt_file:
        with open('cik_ticker.csv', 'w') as csv_file:
            csv_writer = csv.writer(
                csv_file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Ticker', 'cik'])
            for line in txt_file:
                line_split = line.split()
                csv_writer.writerow([line_split[0].upper(), line_split[1]])

    return 'cik_ticker.csv'


def get_ticker_from_yahoo(cusip, try_number=1):
    time.sleep(1/10)
    url = f'https://query1.finance.yahoo.com/v1/finance/search?q={cusip}'
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    request_result = requests.get(url, headers=headers)
    logger.info(f"Getting ticker for {cusip} at {url}")

    try:
        return f"{request_result.json()['quotes'][0]['symbol']}"

    except (KeyError, IndexError) as e:
        return None

    except (requests.exceptions.ConnectionError, ValueError) as e:
        time.sleep(2**try_number + random.random()*0.01)
        try_number += 1
        if try_number >= 20:
            return None

        return get_ticker_from_yahoo(cusip, try_number)

#TODO: use this site instead https://13f.info/cusip/011532108
def get_ticker_from_vanguard(cusip, try_number=1):
    time.sleep(1/2)
    url = f'https://investor.vanguard.com/investment-tools/calculator-tools/marketData?query={cusip}'
    request_result = requests.get(url)
    logger.info(f"Getting ticker for {cusip} at {url}")

    try:
        return f"{request_result.json()['result']['symbol']}"

    except KeyError as e:
        return None

    except (requests.exceptions.ConnectionError, ValueError) as e:
        time.sleep(2**try_number + random.random()*0.01)
        try_number += 1
        if try_number >= 20:
            return None
        return get_ticker_from_vanguard(cusip, try_number)


def find_or_add_to_ticker_csv(cusip):
    with open('csv_with_ticker.csv', 'a', newline='') as csv_file:
        pass

    with open('csv_with_ticker.csv', 'r+', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)

        for row in csv_reader:
            if cusip.upper() in row[0]:
                return row[1]

        csv_writer = csv.writer(csv_file, delimiter=',',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)
        ticker = None
        if ticker is None:
            ticker = get_ticker_from_yahoo(cusip)
        csv_writer.writerow([cusip.upper(), ticker])
        return ticker


def get_source(cusip):
    ticker = find_or_add_to_ticker_csv(cusip)
    return ticker
#########


tracked_companies = []


def get_ticker(company_name):
    soup = get_source(company_name)


def clear_csv(csv_file):
    file = open(csv_file, 'r+')
    file.truncate(0)
    file.close()


def create_2D_graph(csv_file_path, x_label, y_label, title, x_row=0, y_row=1):
    x = []
    y = []

    z = 0
    with open(csv_file_path, 'r') as csvfile:

        plots = csv.reader(csvfile, delimiter=',')

        for row in plots:
            x.append(row[x_row])
            y.append(int(row[y_row]))
            z += 1
            if z > 20:
                break

    plt.bar(x, y, color='g', width=0.72, label="Age")
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
        csv_writer = csv.writer(csv_header, delimiter=',',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['nameOfIssuer', 'cusip', 'value', 'shares', 'sshPrnamtType',
                             'putCall', 'investmentDiscretion', 'otherManager', 'soleVotingAuthority',
                             'sharedVotingAuthority', 'noneVotingAuthority', 'ownedBy', 'ownedByName'])

    lastCik = 0
    lastName = 'filler'
    for file in file_arr:
        try:
            with open(file, 'r', newline='') as csvfile:
                with open(path, 'a', newline='') as csvfilewrite:
                    csv_reader = csv.reader(
                        csvfile, delimiter=',', quotechar='|')
                    next(csv_reader)
                    for row in csv_reader:
                        row[1] = row[1].upper()
                        ownedCompany = file.split('/')[9]
                        row.append(ownedCompany)
                        if lastCik == ownedCompany:
                            row.append(lastName)
                        else:
                            ownedCompanyName = cik_to_company_name(
                                ownedCompany)
                            row.append(ownedCompanyName)
                            lastCik = ownedCompany
                            lastName = ownedCompanyName
                        try:

                            csv_writer = csv.writer(
                                csvfilewrite, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerow(row)
                        except ValueError as e:
                            continue

        except(FileNotFoundError):
            continue

        except(IndexError):
            continue

    return path


def cik_to_company_name(cik, file_to_search='cik_name.csv'):
    with open(file_to_search, 'r', newline='') as file:
        for row in file:
            row = row.split(',')
            if cik == row[0]:
                size = len(row[1])
                # Slice string to remove last 3 characters from string
                formated_name = row[1][:size - 3]
                return formated_name

    return None


def read_all_copmany_names_from_edgar_master(edgar_path, save_path):
    with open(save_path, 'w', newline='') as csv_header:
        csv_writer = csv.writer(csv_header, delimiter=',',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['cik', 'nameOfIssuer'])

    with open(edgar_path, 'r', newline='') as edgar_file:
        with open(save_path, 'a+', newline='') as new_file:
            try:
                for x in range(12):
                    # ignore intro lines
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
        headerList = ['cusip', 'nameOfIssuer', 'Ticker']
        csv_writer = csv.DictWriter(csv_header, delimiter=',',
                                    fieldnames=headerList)
        csv_writer.writeheader()

    with open(save_file, 'a+', newline='') as save_file:
        for key, item in df:
            print(key, item['nameOfIssuer'].iloc[0])
            csv_writer = csv.writer(save_file, delimiter=',',
                                    escapechar=' ', quoting=csv.QUOTE_NONE)
            ticker = get_source(key)
            csv_writer.writerow([key, item['nameOfIssuer'].iloc[0], ticker])

    return save_file

    
def merge_cik_to_cusip(collection_cusip, collection_cik, save_file):
    cusip_df = pandas.read_csv(collection_cusip, header=0, index_col=['nameOfIssuer'])
    cik_df = pandas.read_csv(collection_cik, header=0, index_col=['nameOfIssuer'])
    merged_df = pandas.merge(cik_df, cusip_df, how='outer', on=['nameOfIssuer'])

    merged_df.to_csv(save_file)
    return save_file


def merge_cik_ticker_to_cik_company_name(cik_ticker_file, cik_comany_name_file, save_file='cik_name_ticker.csv'):
    df_ticker = pandas.read_csv(cik_ticker_file, header=0, index_col='cik')
    df_name = pandas.read_csv(cik_comany_name_file, header=0, index_col='cik')
    df_merged = pandas.merge(df_name, df_ticker, how='outer', on=['cik'])
    df_merged.to_csv(save_file)
    return save_file



if __name__ == "__main__":
    company_ciks = read_all_copmany_names_from_edgar_master('Apps/Collection/src/resources/edgar-full-index-archives/master-2020-QTR1.txt',
                                                            'cik_name.csv')
    cik_ticker_csv = get_cik_ticker_to_csv_from_sec()
    cik_name_ticker_csv = merge_cik_ticker_to_cik_company_name(cik_ticker_csv, company_ciks)
    # run cik_name_ticker_csv through source function to get more tickers

    # TODO: collect_13_f_companies_and_shares() should take in the qtr it is looking at
    file_arr = collect_13_f_companies_and_shares()
    print(f"{file_arr} is file array")
    
    file_13f = create_full_qtr_list_of_13f(file_arr, '13f_collection.csv')

    # result is a csv with cusip, company name, and ticker
    # takes in the 13f_collection.csv and looks up ticker and returns cusip,nameOfIssuer,Ticker
    cusip_colection = match_company_names_to_cusip(
        '13f_collection.csv', 'cusip_name_ticker.csv')

    # meges on  name then ticker then fails to match
    merge_cik_to_cusip('cusip_name_ticker.csv','cik_name_ticker.csv',
                        'merged.csv')
