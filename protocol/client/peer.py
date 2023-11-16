import socket 
import os 
import argparse
import pickle 
import threading
import time
import tqdm


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

def publish_file(lname, fname):
    peer.send(b'ACK')

    # recv REC 
    data = peer.recv(BUFFSIZE).decode(FORMAT)
    if data == "REC":  
        with open(lname, 'rb') as f:

            file_size = os.path.getsize(lname)
            
            # # send lname name and date
            # if os.name == 'nt':
            #     file_name = lname.split('\\')[-1]
            # else:
            #     file_name = lname.split('/')[-1]
            peer.send(fname.encode('utf-8')) #1
            # recv ACK
            data = peer.recv(BUFFSIZE)
            
            
            peer.send(str(file_size).encode('utf-8')) #2
            # recv ACK
            data = peer.recv(BUFFSIZE)
            time.sleep(0.00000000000000000000001)
            
            data_sent = 0
            progress = tqdm.tqdm(range(file_size), desc=fname, unit='B', unit_scale=True, unit_divisor=BUFFSIZE)
            while data_sent < file_size:
                file_data = f.read(BUFFSIZE)
                peer.sendall(file_data)
                data_sent += BUFFSIZE
                progress.update(BUFFSIZE)
            progress.desc = f'{fname} Sent'
            progress.close()
            print(fname)
            
        data = peer.recv(BUFFSIZE).decode(FORMAT)

while True:
    msg = input("What do we want to send to the server?: ")
    command = msg.encode(FORMAT)
    peer.send(command)
    message_response = peer.recv(BUFFSIZE)
    print(message_response.decode(FORMAT))
    command = str(msg).split(' ')
    if command[0] == 'publish':
        # threading._start_new_thread(publish_file,args = './media/image.png')
        
        threading.Thread(target = publish_file, args = (command[1],command[2])).start()
        print("[SENDING] successful...")
    elif command[0] == 'fetch':
        pass
    elif command[0]== 'exit':
        peer.close()
        break
    else:
        pass