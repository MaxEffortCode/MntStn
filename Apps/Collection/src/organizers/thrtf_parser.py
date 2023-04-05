import os
import csv

#class that goes into ../resources/* and looks for 13F-HR-data.csv by year and quarter
#then it will parse the data and put it into an array of arrays
# each array will contain the following data:
# nameOfIssuer,cusip,value,shares,sshPrnamtType,putCall,investmentDiscretion,otherManager,soleVotingAuthority,sharedVotingAuthority,noneVotingAuthority
# it will then return the array of arrays
#

#fuck all the arrays, we'l luse the csv library instead
class ThrtFParser:
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.files = []
        self.path = os.path.join(os.path.dirname(__file__), f"../resources/{self.year}/{self.quarter}/companies")
        #self.parseData()

    def get_thrtf_files(self):
        #crawl the path and get all the files with 13F-HR-data.csv
        self.files = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.startswith("13F"):
                    self.files.append(os.path.join(root, file))
        return self.files
    
    def update_year(self, year):
        self.year = year
        self.path = os.path.join(os.path.dirname(__file__), f"../resources/{self.year}/{self.quarter}/companies")
        print(f"\nupdated with year: {self.year} \nnew file path: {self.path}\n")
        self.get_thrtf_files()
        return self.path
    
    def update_quarter(self, quarter):
        self.quarter = quarter
        self.path = os.path.join(os.path.dirname(__file__), f"../resources/{self.year}/{self.quarter}/companies")
        print(f"\nupdated with quarter: {self.quarter} \nnew file path: {self.path}\n")
        self.get_thrtf_files()
        return self.path
        

    
    #function that will run get_thrtf_files and parse the data into an a csv
    #it will take in the path to save the csv to
    #if the csv already exists, it will append the data to the csv without the first line
    def merge_thrtf_files(self):
        #get all the files
        self.get_thrtf_files()
        #open the csv file
        file_save_path = f"/home/max/MntStn/Apps/Collection/src/organizers/../resources/{self.year}/{self.quarter}/13f-collections/"
        #make the directory if it doesn't exist
        if not os.path.exists(os.path.dirname(file_save_path)):
            os.makedirs(os.path.dirname(file_save_path))
            print(f"made directory: {file_save_path}")
        csv_path = os.path.join(os.path.dirname(__file__), f"{file_save_path}/13F-HR-data-{self.year}-{self.quarter}.csv")
        with open(csv_path, 'a') as csv_file:
            #create the writer
            writer = csv.writer(csv_file)
            #clear the file
            csv_file.truncate(0)
            writer.writerow(["nameOfIssuer","cusip","value","shares","sshPrnamtType","putCall","investmentDiscretion","otherManager","soleVotingAuthority","sharedVotingAuthority","noneVotingAuthority"])

            #for each file in the list of files
            for file in self.files:
                #open the file
                
                with open(file, 'r') as thrtf_file:
                    #create the reader
                    reader = csv.reader(thrtf_file)
                    #skip the first line
                    next(reader)
                    #for each line in the file
                    for line in reader:
                        #write the line to the csv
                        writer.writerow(line)                        
        
        #close the csv file
        csv_file.close()
                        
        return csv_path
    
if __name__ == "__main__":
    test = ThrtFParser(2017, 1)
    print(test.get_thrtf_files())
    print(test.update_year(2017))
    print(test.update_quarter(1))
    file_save_path = f"/home/max/MntStn/Apps/Collection/src/organizers/../resources/{test.year}/{test.quarter}/13f-collections/"
    #make the directory if it doesn't exist
    print(test.merge_thrtf_files())
