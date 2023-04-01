#CIK|Company Name|Form Type|Date Filed|Filename

import os
import time

#class that handles the master index file
class master_index_parser:
    def __init__(self, master_index_file_path):
        self.master_index_file_path = master_index_file_path
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
    
    def update_master_index_file(self, new_index_file_path):
        self.master_index_file.close()
        self.master_index_file_path = new_index_file_path
        self.master_index_file = open(self.master_index_file_path, "r")
        print("Updated Master Index File Path: " + self.master_index_file_path)
        
    #returns array(s) from selected CIK[0]|Company Name[1]|Form Type[2]|Date Filed[3]|Filename[4]
    def create_arrays(self, cik=False, company_name=False, form_type=False, date_filed=False, filename=False):
        if cik:
            cik_array = []
        if company_name:
            company_name_array = []
        if form_type:
            form_type_array = []
        if date_filed:
            date_filed_array = []
        if filename:
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
            


if __name__ == '__main__':
    #the path is ../resources/edgar-full-index-archives/master-2017-QTR1.txt
    master_index_file_path = os.path.join(os.path.dirname(__file__), "../resources/edgar-full-index-archives/master-test-file.txt")
    master_index_file = master_index_parser(master_index_file_path)
    print(master_index_file.get_next_line())
    print(master_index_file.index_begin_company_list())
    print(master_index_file.create_arrays(cik=True, company_name=True, form_type=True, date_filed=True, filename=True))
    