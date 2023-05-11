import sys
import path

directory = path.Path(__file__).abspath()
print(directory)
sys.path.append(directory.parent.parent)
from organizers import master_index_parser, thrtf_parser
from appenders import ticker


# class that runs the appenders and organizers
# over every company directory in the resources folder
class run_appenders_and_organizers:
    #constructor
    def __init__(self, year, quarter):
        self.year = year
        self.quarter = quarter
        self.master_index_parser = master_index_parser.master_index_parser(self.year, self.quarter)
        self.thrtf_parser = thrtf_parser.ThrtFParser(self.year, self.quarter)
        self.ticker = ticker.Ticker(self.year, self.quarter)
        
    #function that runs the appenders and organizers
    #over every company directory in the resources folder
    def run(self):
        
        self.master_index_parser.index_to_csv()
        self.master_index_parser.index_to_csv_no_duplicates()
        self.master_index_parser.index_to_csv_no_duplicates_companies()
        self.thrtf_parser.merge_thrtf_files()
        self.ticker.append_tickers_to_cik_name()
    
if __name__ == '__main__':
    #run the appenders and organizers
    run_appenders_and_organizers(2020, 1).run()
    run_appenders_and_organizers(2020, 2).run()
    run_appenders_and_organizers(2020, 3).run()
    run_appenders_and_organizers(2020, 4).run()