#CIK|Company Name|Form Type|Date Filed|Filename

import os
import csv
import time

#class that handles the master index file
class master_index_parser:
    def __init__(self, year, quarter):
        path = f"{os.path.dirname(__file__)}/../resources/edgar-full-index-archives"
        edgarIndexFileDownloadPath = f"{path}/master-{year}-QTR{quarter}.txt"
        self.master_index_file_path = edgarIndexFileDownloadPath
        self.year = year
        self.quarter = quarter
        self.master_index_file = open(self.master_index_file_path, "r")
        print("Created an master_index_parser object\n with Master Index File Path: " + self.master_index_file_path)

    def get_next_line(self):
        return self.master_index_file.readline()
    
    def index_begin_company_list(self):
        self.master_index_file.seek(0)
        current_line = 0
        current_line_string = ""
        while "CIK" not in current_line_string:
            #print(f"skipping line {current_line} with string {self.master_index_file.readline()}")
            #self.master_index_file.readline()
            current_line += 1
            current_line_string = self.master_index_file.readline()

        self.master_index_file.readline()
        self.master_index_file.readline()
        current_line += 2
        
        return current_line
    
    def set_line(self, line_number):
        self.master_index_file.seek(0)
        for i in range(line_number):
            self.master_index_file.readline()
        
        return self.master_index_file
    
    '''
    This function will take in a csv file path and will write the data from the master index file to the csv
    it will use csv reader to read the master index file starting at index_begin_company_list
    from there each line will be split by the | character and the data will be appended to the csv
    '''
    def index_to_csv(self):
        look_up_dir = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/13f_collection"
        #create lookup directory if it does not exist
        if not os.path.exists(look_up_dir):
            os.makedirs(look_up_dir)
        lookup_file_path = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/13f_collection/master.csv"
        
        
        with open(lookup_file_path, 'a') as csv_file:
            writer = csv.writer(csv_file)
            csv_file.truncate(0)
            writer.writerow(["cik","company Name","form type","date filed","filename"])
            company_list_start = self.set_line(self.index_begin_company_list())
            
            for line in company_list_start:
                line_split = line.split("|")
                line_split[-1] = line_split[-1].strip()
                #strip any ""
                #TODO: there is a bug where if the company name has a . at the end it will be be given quotes
                line_split = [x.strip('"') for x in line_split]
                writer.writerow(line_split)
            
            print("Wrote to CSV file: " + lookup_file_path)
            csv_file.close()
            
        return lookup_file_path 
    
    def update_master_index_file(self, new_index_file_path):
        self.master_index_file.close()
        self.master_index_file_path = new_index_file_path
        self.master_index_file = open(self.master_index_file_path, "r")
        print("Updated Master Index File Path: " + self.master_index_file_path)
        
    #returns array(s) from selected CIK[0]|Company Name[1]|Form Type[2]|Date Filed[3]|Filename[4]
    def create_arrays(self, cik=False, company_name=False, form_type=False, date_filed=False, filename=False):
        cik_array = []
        company_name_array = []
        form_type_array = []
        date_filed_array = []
        filename_array = []
        
        company_list_start = self.set_line(self.index_begin_company_list())
        
        for line in company_list_start:
            line_split = line.split("|")
            if cik:
                cik_array.append(line_split[0])
            if company_name:
                company_name_array.append(line_split[1])
            if form_type:
                form_type_array.append(line_split[2])
            if date_filed:
                date_filed_array.append(line_split[3])
            if filename:
                filename_array.append(line_split[4])
        
        #merge arrays into one array split by [] and return
        return [cik_array, company_name_array, form_type_array, date_filed_array, filename_array]
    
    #function that takes in self
    #it grabs the CIK, Company Name,
    #it only appends the CIK and Company Name to the csv file if the CIK is not already in the csv file
    #the csv file is saved under lookup file path
    def index_to_csv_no_duplicates(self):
        look_up_dir = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup"
        #create lookup directory if it does not exist
        if not os.path.exists(look_up_dir):
            os.makedirs(look_up_dir)
        lookup_file_path = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup/cik_name.csv"
        
        with open(lookup_file_path, 'a') as csv_file:
            
            writer = csv.writer(csv_file)
            csv_file.truncate(0)
            writer.writerow(["cik","company Name"])
            company_list_start = self.set_line(self.index_begin_company_list())
            
            old = ""
            for line in company_list_start:
                line_split = line.split("|")
                new = line_split[0]

                while new == old:
                    line_split = company_list_start.readline().split("|")
                    new = line_split[0]

                old = new
                try:
                    writer.writerow([line_split[0], line_split[1]])
                except(IndexError):
                    break
            
            print("Wrote to CSV file: " + lookup_file_path)
            csv_file.close()
        
        return lookup_file_path
    
    def index_to_csv_no_duplicates_companies(self):
        look_up_dir = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup"
        #create lookup directory if it does not exist
        if not os.path.exists(look_up_dir):
            os.makedirs(look_up_dir)
        lookup_file_path = f"{os.path.dirname(__file__)}/../resources/{self.year}/{self.quarter}/lookup/name.csv"
        
        with open(lookup_file_path, 'a') as csv_file:
            
            writer = csv.writer(csv_file)
            csv_file.truncate(0)
            writer.writerow(["company Name"])
            company_list_start = self.set_line(self.index_begin_company_list())
            
            old = ""
            try:
                for line in company_list_start:
                    line_split = line.split("|")
                    new = line_split[0]

                    while new == old:
                        line_split = company_list_start.readline().split("|")
                        new = line_split[0]

                    old = new
                    try:
                        writer.writerow([line_split[1]])
                    except(IndexError):
                        break
            except(UnicodeDecodeError):
                print("UnicodeDecodeError")

                
            
            print("Wrote to CSV file: " + lookup_file_path)
            csv_file.close()
        
        return lookup_file_path
                


if __name__ == '__main__':
    #the path is ../resources/edgar-full-index-archives/master-2017-QTR1.txt
    """ 
    test = master_index_parser(2020, 1)
    print(test.get_next_line())
    print(test.index_begin_company_list())
    print(test.create_arrays(cik=True, company_name=True, form_type=True, date_filed=True, filename=True))

    file_save_path = f"/home/max/MntStn/Apps/Collection/src/organizers/../resources/{test.year}/{test.quarter}/master_index/"
    if not os.path.exists(os.path.dirname(file_save_path)):
        os.makedirs(os.path.dirname(file_save_path))
        print(f"made directory: {file_save_path}")
    print(test.index_to_csv())
    print(test.index_to_csv_no_duplicates())
    print(test.index_to_csv_no_duplicates_companies())
     """
    for i in range(1993, 2023):
        for j in range(1, 5):
            test = master_index_parser(i, j)
            print(test.index_to_csv_no_duplicates_companies())
            time.sleep(1/10)
            