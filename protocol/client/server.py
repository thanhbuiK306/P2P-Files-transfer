import socket
import os 
import tqdm
import argparse
import threading 
import pickle
import select 

from client import Client
from share_file_handler import handshake_impl

peers_list =[]
BUFFSIZE = 2048

FORMAT = 'utf-8'
lock  = threading.Lock()
def server_command_executor():
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
def client_command_executor(conn):
    while True: 
        conn.setblocking(0)
        ready = select.select([conn], [], [], 1)
        if ready[0]:
            conn.settimeout(10)
            request = conn.recv(BUFFSIZE).decode(FORMAT)
            request = str(request).split(' ')

            if request[0] == 'publish':
                message_response = str("Server ready to be get file...").encode(FORMAT)
                conn.send(message_response)
                
            elif request[0] == 'fetch':
                lock.acquire()
                message_response = str("Server ready to be provide communication...").encode(FORMAT)
                conn.send(message_response)
                threading.Thread(target = handshake_impl, args= (conn,peers_list[0])).start()
                lock.release()
            elif request[0]== 'exit':
                conn.close()
                break
            else:
                print("hehe")
                message_response = str("Command incorrectly, please input another statement...").encode(FORMAT)
                conn.send(message_response)
def on_new_conn(conn, addr):
    ip = addr[0]
    port = addr[1]
    peers_list.append((ip,port,conn))
    conn.send(ip.encode(FORMAT))
    conn.send(str(port).encode(FORMAT))
    print(f"THe new addr was made from IP: {ip}, and port: {port}!")
    threading._start_new_thread(client_command_executor,(conn,))