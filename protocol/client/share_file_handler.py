import socket 
import os 
import argparse
import pickle 
import threading
from threading import Lock
import time
import tqdm

from peer import peer
from peer_socket import peerSock
HEADER = 64
FORMAT = 'utf-8'
BUFFSIZE = 2048
lock = Lock()
def handshake_impl(clientRequest, clientHost):
    # Handshake with the client
    lock.acquire()
    ip, port, host = clientHost
    msgg= "ngon" 
    host.send(msgg.encode(FORMAT)) #signal peerhost that a client want to fetch a file
    # host send message to confirm they are accept to send file
    #host send #1
    host.settimeout(5)
    #host receive #2
    message_response = host.recv(BUFFSIZE).decode(FORMAT) # chua nhan duoc ack co the la do recv_request timeout qua lau
    print("host ack", message_response)
    
    # client send message that they are receive ip and port of peer 
    #client send #1
    clientRequest.send(ip.encode(FORMAT))
    clientRequest.settimeout(5)
    #client receive #2
    message_response = clientRequest.recv(BUFFSIZE).decode(FORMAT)
    print("conn ack ", message_response)
    #client send #3
    clientRequest.send(str(port).encode(FORMAT))
    
    clientRequest.settimeout(5)
    #client receive #4
    clientRequest.recv(BUFFSIZE)
    # gui den host la client san sang ket noi
    #server send to host #3
    host.send(b"ACK")
    #
    host.settimeout(5)
    # host receive #4 that host initialize success
    host.recv(BUFFSIZE)
    #server send to client send #5 that hay ket noi di
    clientRequest.send(b"ACK")
    #
    clientRequest.settimeout(5)
    #client receive #6 
    clientRequest.recv(BUFFSIZE)
    #server send to host #5 to accept connection
    host.send(b"ACK")
    lock.release()
def p2p_file_transfer():
    pass
