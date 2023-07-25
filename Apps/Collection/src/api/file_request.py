import socket
import sys
import threading
import time
#exec(open("Apps/Collection/src/api/file_request.py").read())
#export PYTHONPATH=/home/max/Mountain_Stone_LLC/MntStn:$PYTHONPATH
#from file_request_handler import FileReqHandler
from Apps.Collection.src.api.file_request_handler import FileReqHandler
#from file_request_handler import FileReqHandler

### Server Side ###
#HOST = '127.0.0.1'  # The server's hostname or IP address
#HOST = '0.0.0.0'
HOST = '34.125.225.88'
PORT = 8000       # The port used by the server

def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(2048)
            if not data:
                break
            print(f'Received from {addr}: {data}')
            #data_tuple = data.decode().split(",")
            #print(f"Data tuple: {data_tuple}")
            search_type, search_term, year, quarter = data.decode().split(',')
            file_req_handler = FileReqHandler(year, quarter)

            if search_type == "name":
                company_cik = file_req_handler.get_file_company_name(f"{search_term}")
                file_path = file_req_handler.get_file_cik(company_cik, "13F-HR")
            
            elif search_type == "cik":
                company_cik = search_term
                file_path = file_req_handler.get_file_cik(company_cik, "13F-HR")

            elif search_type == "ticker":
                conn.sendall(b'No ticker support yet')
                return False

            else:
                conn.sendall(b'Invalid search type. Valid search types are: name, cik, ticker')
                return False
                
            #file_path = file_req_handler.get_file_cik(company_cik, "13F-HR")
            print(f"\n**** Saved to {file_path} ****\n")
            
            with open(file_path[0], 'rb') as f:
                data = f.read()
            
            if data:
                conn.sendall(data)
                return
            else:
                print("No data")
                return


if __name__ == '__main__':
    print("Starting server...")
    time.sleep(0.2)
    
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
    
    else:
        HOST = input("Enter host IP: ")
        PORT = int(input("Enter port: "))


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
