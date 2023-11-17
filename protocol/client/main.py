import socket 
import os 
import argparse
import pickle 
import threading
import time
import tqdm

from peer import publish_file
parser = argparse.ArgumentParser(description = "This is the peer for the multi threaded socket server!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 5000)
args = parser.parse_args()

print(f"Connecting to server: {args.host} on port: {args.port}")

HEADER = 64
FORMAT = 'utf-8'
BUFFSIZE = 2048

peer =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    peer.connect((args.host, args.port))
    Message = peer.recv(BUFFSIZE).decode(FORMAT)
    print(Message)
except Exception as e:
    raise SystemExit(f"We have failed to connect to host: {args.host} on port: {args.port}, because: {e}")
def command_executor():
    while True:
        msg = input("What do we want to send to the server?: ")
        command = msg.encode(FORMAT)
        peer.send(command)
        message_response = peer.recv(BUFFSIZE)
        print(message_response.decode(FORMAT)) # change message to ACK or DACK 
                                               # then check condition before write command line
        command = str(msg).split(' ')
        if command[0] == 'publish':
            # threading._start_new_thread(publish_file,args = './media/image.png')
            
            threading.Thread(target = publish_file, args = (peer, command[1],command[2])).start()
            print("[SENDING] successful...")
        elif command[0] == 'fetch':
            pass
        elif command[0]== 'exit':
            peer.close()
            break
        else:
            pass
if __name__ =='__main__':
    command_executor()