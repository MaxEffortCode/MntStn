import socket
import threading
from Apps.Collection.src.api.file_request_handler import FileReqHandler

### Server Side ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433        # The port used by the server

def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f'Received from {addr}: {data}')
            file_req_handler = FileReqHandler("2019", "4")
            company_cik = file_req_handler.get_file_company_name("BROOKFIELD ASSET MANAGEMENT INC.")
            file_path = file_req_handler.get_file_cik(company_cik, "13F-HR")
            #print file path
            print(f"Sending to {addr}: {file_path}")


            print(f"Sending to {addr}: {file_req_handler.get_file_company_name('META GROUP INC')}")
            conn.sendall(file_req_handler.get_file_company_name('META GROUP INC').encode())
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