import os
import sys
import csv
import time



#class searcher that takes in an array and a search term
# it will return the closest match to the search term
# it will have a variety of methods to find the closest match
class Searcher:
    def __init__(self, array, search_term):
        self.array = array
        self.search_term = search_term

    #function that takes in self
    #it will return the closest match to the search term
    #it will have a variety of methods to find the closest match
    def search(self):
        #if the search term is a CIK
        if self.search_term.isdigit():
            #if the search term is in the array
            if self.search_term in self.array:
                #return the search term
                return self.search_term
            #if the search term is not in the array
            else:
                #return none
                return None
        #if the search term is not a CIK
        else:
            #return the closest match
            return self.closest_match()

    #function that takes in self
    #it will return the closest match to the search term
    #it will have a variety of methods to find the closest match
    def closest_match(self):
        #time the different methods
        #time the levenshtein distance method
        closest_match = ""
        start = time.time()
        closest_match = self.closest_match_levenshtein()
        end = time.time()
        print(f"Levenshtein Distance time: {end - start}\nLevenshtein Distance closest match: {closest_match}\n")
        
        
        return closest_match

    #function that takes in self
    #it will return the closest match to the search term
    #it will have a variety of methods to find the closest match
    def closest_match_levenshtein(self):
        #set the closest match to none
        closest_match = None
        #set the closest match distance to the length of the search term
        closest_match_distance = len(self.search_term)
        #for each item in the array
        for item in self.array:
            #set the distance to the levenshtein distance between the search term and the item
            distance = self.levenshtein_distance(self.search_term, item)
            #if the distance is less than the closest match distance
            if distance < closest_match_distance:
                #set the closest match to the item
                closest_match = item
                #set the closest match distance to the distance
                closest_match_distance = distance
        #return the closest match
        return closest_match

    #function that takes in self, a, and b
    #it will return the levenshtein distance between a and b
    def levenshtein_distance(self, a, b):
        #if a is empty
        if len(a) == 0:
            #return the length of b
            return len(b)
        #if b is empty
        if len(b) == 0:
            #return the length of a
            return len(a)
        #set the first row to the length of a
        first_row = range(len(a) + 1)
        #for each item in b
        for i, c1 in enumerate(b):
            #set the second row to the length of a
            second_row = [i + 1]
            #for each item in a
            for j, c2 in enumerate(a):
                #if the item in a is equal to the item in b
                if c1 == c2:
                    #set the second row to the first row
                    second_row.append(first_row[j])
                #if the item in a is not equal to the item in b
                else:
                    #set the second row to the minimum of the first row, the second row, and the first row
                    second_row.append(1 + min((first_row[j], first_row[j + 1], second_row[-1])))
            #set the first row to the second row
            first_row = second_row
        #return the last item in the first row
        return first_row[-1]
        
    


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
        name_array = []
        with open(self.cik_name_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                name_array.append(row[1])
                if row[1].upper() == name.upper():
                    return row[0]
            
            print(f"Name not found: {name}")
            #do a bunch of AI stuff to find the closest match
            search = Searcher(name_array, name)
            closest_match = search.search()
            print(f"Closest match: {closest_match}")
            if closest_match is not None:
                return self.search_name(closest_match)

            return None

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
    search = SearchAndFind(2017, 1)
    print(search.search_cik('946563'))
    print(search.search_ticker('AAPL'))
    print(search.search_name('BINdwawd'))
