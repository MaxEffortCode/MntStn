import socket
import threading
from Apps.Collection.src.api.file_request_handler import FileReqHandler
import os

### Server Side ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

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

            #print(f"Sending to {addr}: {file_req_handler.get_file_company_name('BROOKFIELD ASSET MANAGEMENT INC.')}")
            #conn.sendall(file_req_handler.get_file_company_name('BROOKFIELD ASSET MANAGEMENT INC.').encode())
            #conn.sendall(data)

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()