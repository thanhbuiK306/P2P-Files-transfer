import socket
import threading
import select
import tqdm
import os
import sys
from time import sleep, time
from queue import Queue

BUFFSIZE = 1024
class peerSock():
    def __init__(self, peerIP, peerPort, pSocket = None):
        if pSocket is None:
            self.peerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #peer host
            self.peer_connection = False
        else:
            self.peer_connection = True
            self.peerSock= pSocket
        
        self.timeout = 999
        self.peerSock.settimeout(self.timeout)
        
        # IP and port of the self.peerSock
        self.IP         = peerIP
        self.port       = peerPort
        self.unique_id  = self.IP + ' ' + str(self.port)

        #IP and port of the peer need communication
        self.peerIP = ""
        self.peerPort = None
        # the maximum self.peerSock request that seeder can handle
        self.max_peer_requests = 50
        # queue peer pending 
        self.peer_list = Queue(maxsize=self.max_peer_requests)
        # socket locks for synchronization 
        self.socket_lock = threading.Lock()
    #before send data validate user ready to receive or self.peerSock socket has been connect
    def recv(self):
        return self.peerSock.recv(BUFFSIZE).decode('utf-8')
    def send_data(self,lname, fname ):
        if self.peer_list.empty():
            print("vcb")
            return False 
        with open(lname, 'rb') as f:
            file_size = os.path.getsize(lname)
            # self.peerSock.send(fname.encode('utf-8')) #1
            # recv ACK - validate peer connection has recv fname
            data = self.peerSock.recv(BUFFSIZE) #1
            if data != b'ACK':
                pass
            self.peerSock.send(str(file_size).encode('utf-8')) #2
            # recv ACK - validate peer connection has recv file_size
            data = self.peerSock.recv(BUFFSIZE) #2
            if data != b'ACK':
                pass
            time.sleep(0.00000000000000000000001)
            
            data_sent = 0
            progress = tqdm.tqdm(range(file_size), desc=fname, unit='B', unit_scale=True, unit_divisor=BUFFSIZE)
            while data_sent < file_size:
                try:
                    file_data = f.read(BUFFSIZE)
                    self.peerSock.sendall(file_data)
                    data_sent += BUFFSIZE
                    progress.update(BUFFSIZE)
                except:
                    #the TCP connection is broken
                    progress.desc = f'{fname} Unsuccessfully send'
                    progress.close()
                    return False
            progress.desc = f'{fname} Sent'
            progress.close()
            print("Data sent: ",data_sent)
            return True

    def receive_data(self, fname):
        
        if not self.peer_list.empty():
            return 
        peerRequest = self.peer_list.get()   
        peerRequest.send(b'ACK') #1

        file_size = peerRequest.recv(BUFFSIZE)
        peerRequest.send(b'ACK') #2
        file_size = int(file_size)
        print(file_size)
        peer_raw_data = b''
        received_data_length = 0
        request_size = file_size
         # loop untill you recieve all the data from the peer
        progress = tqdm.tqdm(range(file_size), desc=f"Receiving {fname}", unit='B', unit_scale=True, unit_divisor=BUFFSIZE)
        while(received_data_length < file_size):
            # attempt recieving requested data size in chunks
            try:
                chunk = peerRequest.recv(BUFFSIZE)
            except:
                chunk = b''
            if len(chunk) == 0:
                return None
            
            progress.update(chunk)
            peer_raw_data += chunk
            request_size -=  len(chunk)
            received_data_length += len(chunk)
        progress.desc = f"{fname} Received"
        progress.close()
        print("data received: ",received_data_length)
        file_path = os.path.join(self.save_dir, fname)
        with open(file_path, 'wb') as f:
            f.write(peer_raw_data)
        return peer_raw_data
        # return required size data recieved from peer
    def p2p_file_transfer(self, ip , port ):
        pass
    def start_seeding(self):
        try:
            self.peerSock.bind((self.IP, self.port))
            self.peerSock.listen(self.max_peer_requests)
        except Exception as err:
            print(err)
            # binding_log = 'Seeding socket binding failed ! ' + self.unique_id + ' : '
            # self.socket_logger.log(binding_log + err.__str__())
            sys.exit(0)
    def request_connection(self, ip, port):
        try:
            self.peerSock.connect((ip,port)) #addr of peer, peerSock is current
            self.peerIP = ip
            self.peerPort = port
            self.peer_connection = True
        except Exception as err:
            self.peer_connection = False
            print(err)
            # connection_log = 'Socket connection failed for ' + self.unique_id + ' : '
            # self.socket_logger.log(connection_log + err.__str__())
        return self.peer_connection
    def accept_connection(self):
        #connection_log = ''
        try:
            connection, addr = self.peerSock.accept()
            self.peer_list.put(connection)
            print(self.peer_list.qsize())
            # connection_log += 'Socket connection recieved !'
        except Exception as err:
            connection = None
            # connection_log = 'Socket accept connection for seeder ' + self.unique_id + ' : ' 
            # connection_log += str(err)
        # self.socket_logger.log(connection_log)
        # successfully return connection
        return connection
    def peer_connection_active(self):
        return self.peer_connection
    # def p2p_file_transfer(self, lname ,fname):
    #     print("step 2 success")
    #     threading.Thread(target=self.send_data ,args= (lname, fname)).start()
    #     threading.Thread(target= self.receive_data , args =(fname,)).start()
    #     print("Successful")
        
    def close_connection(self):
        self.peerSock.close() 
        self.peer_connection = False
    def __exit__(self):
        self.close_connection()