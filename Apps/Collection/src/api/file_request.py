import socket
import threading

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433        # The port used by the server

def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Server listening on {HOST}:{PORT}')
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()