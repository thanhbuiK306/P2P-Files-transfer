import socket 
import os 
import argparse
import pickle 
import threading
import time
import tqdm

from client import Client
parser = argparse.ArgumentParser(description = "This is the client for the multi threaded socket server!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 5000)
args = parser.parse_args()



HEADER = 64
FORMAT = 'utf-8'
BUFFSIZE = 2048


def command_executor(client):
    while True:
        
        msg = input("What do we want to send to the server?: ")
        client.send(msg)
        command = str(msg).split(' ')
        if command[0] == 'publish':
            # threading._start_new_thread(publish_file,args = './media/image.png')
            
            # threading.Thread(target = publish_file, args = (client, command[1],command[2])).start()
            print("[SENDING] successful...")
        elif command[0] == 'fetch':
            message_respone = client.recv()
            print(message_respone)
            #client receive #1
            peerHost_ip =  client.recv()
            #client send #2
            client.send(b"ACK")
            #client receive #3
            peerHost_port= client.recv()    
            print(peerHost_ip, peerHost_port)
            
            # client send ack that receive ip and port
            #client send to server #4
            client.send(b"ACK")
            
            #client #receive 5 de ket noi den host
            client.recv()
            
            client.send_connection(peerHost_ip, int(peerHost_port))
            #client send to server #6 to signal send connection success
            client.send(b"ACK")
            #
            # msg = client.peer.recv()
            # print(msg)
            
            client.peer.peerSock.send(b"ACK")
            #client.receive_data('image-copy.png')
            #send    
        elif command[0]== 'exit':
            client.close_server_connection()
            break
        else:
            message_respone = client.recv()
            print(message_respone)

        
if __name__ =='__main__':
    client = Client(args.host, args.port)
    threading.Thread(target = command_executor, args = (client,)).start()
    threading.Thread(target = client.recv_request).start()