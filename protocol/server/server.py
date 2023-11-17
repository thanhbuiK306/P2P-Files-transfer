import socket
import os 
import tqdm
import argparse
import threading 
import pickle

list_conn_ip = []
list_conn_port = []
BUFFSIZE = 2048

FORMAT = 'utf-8'
def fetch_file(client:socket.socket):

    # send REC packet to confirm reception
    save_dir = 'local/'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # recv ack
    data = client.recv(BUFFSIZE).decode(FORMAT)
    print(data)
    client.send(b'REC')
    
    # accept file data
    file_name = client.recv(BUFFSIZE).decode('utf-8')
    print(file_name)
    client.send(b'ACK')

    file_size = client.recv(BUFFSIZE)
    client.send(b'ACK')
    file_size = int(file_size)
    print(file_size)

    file_data = b''
    progress = tqdm.tqdm(range(file_size), desc=f"Receiving {file_name}", unit='B', unit_scale=True, unit_divisor=1024)
    while len(file_data) < file_size:
        data = client.recv(BUFFSIZE)
        file_data += data
        progress.update(BUFFSIZE)
    progress.desc = f"{file_name} Received"
    progress.close()

    file_path = os.path.join(save_dir, file_name)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    data = client.recv(BUFFSIZE)

def server_command_executor():
    print("Server side... ")
    while True:
        command  = input()
        command = command.split(' ')      
        if command[0] == 'discover':
            print("[DISCOVER] hostname")
        elif command[0] == 'ping':
            print("[PING] hostname")
        elif command[0] =='exit':
            print("[EXIT] successfull, all connetion has been closed")
            break
        else:
            print("[INCOMPLETE] command not found")
def client_command_executor(conn,addr):
    while True:
        request = conn.recv(BUFFSIZE).decode(FORMAT)
        request = str(request).split(' ')
        if request[0] == 'publish':
            message_response = str("Server ready to be get file...").encode(FORMAT)
            conn.send(message_response)
            fetch_file(conn)
            
        elif request[0] == 'fetch':
            message_response = str("Server ready to be provide communication...").encode(FORMAT)
            conn.send(message_response)
        elif request[0]== 'exit':
            conn.close()
            break
        else:
            message_response = str("Command incorrectly, please input another statement...").encode(FORMAT)
            conn.send(message_response)
def on_new_conn(conn, addr):
    ip = addr[0]
    port = addr[1]
    list_conn_ip.append(addr[0])
    list_conn_port.append(addr[1])
    print(f"THe new addr was made from IP: {ip}, and port: {port}!")
    
    threading._start_new_thread(client_command_executor,(conn, addr))