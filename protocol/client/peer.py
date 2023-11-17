import socket 
import os 
import argparse
import pickle 
import threading
import time
import tqdm




HEADER = 64
FORMAT = 'utf-8'
BUFFSIZE = 2048


def publish_file(peer, lname, fname):
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

