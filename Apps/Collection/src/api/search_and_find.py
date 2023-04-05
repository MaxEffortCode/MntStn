import os
import sys
import csv

# search_and_find.py
# search is a class that takes a year and quarter and a search term
# the search term can be a CIK, company name, or ticker
# if it is a company name it will search the name.csv file
# if it is found it will return the CIK
# if it is not found it will return the closest match
# the closest match is found by a variety of methods
# we will time each method and return the method that takes the least amount of time
# if it is a CIK it will search the cik_name.csv file
# if it is found it will return the cik else it will none
# if it is a ticker it will search the ticker.csv file
# if it is found it will return the CIK else it will return none


class SearchAndFind:
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.cik_name_file = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup/cik_name.csv"
        self.name_file = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup/name.csv"
        self.ticker_file = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup/tickers.csv"

    def __repr__(self):
        return f"SearchAndFind({self.year}, {self.quarter})"


    def update_year(self, year):
        self.year = year

    def update_quarter(self, quarter):
        self.quarter = quarter

    def search_name(self, name):
        with open(self.cik_name_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[1] == name.upper():
                    return row[0]
            
            else:
                #do a bunch of AI stuff to find the closest match
                closest_match = 'ABERCROMBIE GEORGE B'
                return self.search_name(closest_match)

    def search_ticker(self, ticker):
        with open(self.ticker_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == ticker.lower():
                    return row[1]
            return None

    def search_cik(self, cik):
        # search cik_name.csv file
        # use csv reader to read the file
        # if the search term is found return the cik
        # else return none
        with open(self.cik_name_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == cik:
                    return row[0]
            return None


if __name__ == "__main__":
    search = SearchAndFind(2017, 1,)
    print(search.search_cik('946563'))
    print(search.search_ticker('AAPL'))
    print(search.search_name('ABERCROdawdBIE GEORGE B'))
