from ast import Break
import matplotlib.pyplot as plt
import os
import csv
import hashTable

tracked_companies = []

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
        if sub[2]:
            end_file = sub[2]
            end_file = str(end_file)
            end_file = end_file[2:-2]
            location = f"{sub[0]}/{end_file}"

            data_locations.append(location)
      
    return [sub for sub in data_locations]



def collect_shares(file_arr):
    companies_bought = hashTable.HashTable(50000)
    for file in file_arr:
        try:
            with open(file, newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(csv_reader)
                for row in csv_reader:
                    #3rd element is 'value' of shares bought in thousands so times by a 100
                    #4th element is 'shares' shares owned so (value*1000)/(shares) = price per share they bought at
                    act_val_of_shares = int(row[2])
                    act_val_of_shares = act_val_of_shares*1000
                    amount_of_shares_bought = int(row[3])
                    price_per_share = act_val_of_shares/amount_of_shares_bought
                    stock = row[0]
                    #print(f"stock: {row[0]}, value of collective shares {act_val_of_shares}, amount of shares bought {row[3]}")
                    #print(f"bought for {price_per_share}")
                    if companies_bought.get_val(stock) == None:
                        companies_bought.set_val(stock, amount_of_shares_bought)
                        tracked_companies.append(stock)
                                            
                    else:
                        tot_shares_prch = companies_bought.get_val(stock)
                        tot_shares_prch += amount_of_shares_bought
                        companies_bought.delete_val(stock)
                        companies_bought.set_val(stock, tot_shares_prch)
                        
        except(FileNotFoundError):
            continue
        
        except(IndexError):
            continue
        
        except(ZeroDivisionError):
            continue
    
    return companies_bought


def collect_share_prices(file_arr):
    companies_bought = hashTable.HashTable(50000)
    for file in file_arr:
        try:
            with open(file, newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(csv_reader)
                for row in csv_reader:
                    #3rd element is 'value' of shares bought in thousands so times by a 100
                    #4th element is 'shares' shares owned so (value*1000)/(shares) = price per share they bought at
                    act_val_of_shares = int(row[2])
                    act_val_of_shares = act_val_of_shares*1000
                    amount_of_shares_bought = int(row[3])
                    price_per_share = act_val_of_shares/amount_of_shares_bought
                    stock = row[0]
                    #print(f"stock: {row[0]}, value of collective shares {act_val_of_shares}, amount of shares bought {row[3]}")
                    #print(f"bought for {price_per_share}")
                    if companies_bought.get_val(stock) == None:
                        companies_bought.set_val(stock, price_per_share)
                        tracked_companies.append(stock)
                                            
                    else:
                        tot_shares_price = companies_bought.get_val(stock)
                        tot_shares_price += price_per_share
                        companies_bought.delete_val(stock)
                        companies_bought.set_val(stock, tot_shares_price)
                        
        except(FileNotFoundError):
            continue
        
        except(IndexError):
            continue
        
        except(ZeroDivisionError):
            continue
    
    return companies_bought

if __name__ == "__main__":
    file_arr = collect_13_f_companies_and_shares()
    cmp_shrs_tot = collect_shares(file_arr)
    shares_price_total = collect_share_prices(file_arr)
    tracked_companies.sort()
    
    with open('shares_bought.csv', 'w', newline='') as csvfile:    
        for comp in tracked_companies:
            print(comp)
            print(cmp_shrs_tot.get_val(comp))
            print(shares_price_total.get_val(comp), end="\n\n")
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([comp, cmp_shrs_tot.get_val(comp), shares_price_total.get_val(comp)])
    
    create_2D_graph('shares_bought.csv', x_label='Companies', y_label='Shares Bought', title='stocks from 2022 Q1', x_row=0, y_row=1)