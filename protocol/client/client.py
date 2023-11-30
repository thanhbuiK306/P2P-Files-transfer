import threading 
import os
import socket
from peer_socket import peerSock
import select

HEADER = 64
FORMAT = 'utf-8'
BUFFSIZE = 2048

class Client():
    def __init__(self, serverIP, serverPort):

        #client is connection to server
        #unique_id is addr information to server
        self.client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((serverIP, serverPort))
        except Exception as e:
            raise SystemExit(f"We have failed to connect to host: {serverIP} on port: {serverPort}, because: {e}")
        self.IP = self.client.recv(BUFFSIZE).decode(FORMAT)
        self.port= int(self.client.recv(BUFFSIZE).decode(FORMAT))
        self.unique_id = self.IP +'-'+ str(self.port)
        
        #peerSocket
        self.peer = peerSock(self.IP, self.port)
        #create local folder for storing file identify by unique_id
        self.save_dir = 'local/'+self.unique_id
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
    #implement client function
    def recv_request(self):
        while self.client: 
            self.client.setblocking(10)
            ready = select.select([self.client], [], [], 1)
            if ready[0]:
                self.client.setblocking(10)
                #host receive #1
                request = self.client.recv(BUFFSIZE).decode(FORMAT)
                if request == "ngon":
                    print("ngon that")
                    #chat voi client request la ack" host send #2
                    msg= "ack"
                    self.client.send(msg.encode(FORMAT))
                    # client Request gui toi ack la no da san sang nhan file
                    #host receive of server #3
                    self.client.settimeout(5)
                    self.client.recv(BUFFSIZE)
                    #
                    self.initialize_seeding()
                    # host send to server #4 to ack that initialize susccess
                    self.client.send(b"ACK")
                    #
                    # self.client.settimeout(5)
                    # self.client.recv(BUFFSIZE)
                    
                    peerRequest = self.receive_connection()
                    # self.peer_list.put(peerRequest)
                    #
                    msg = peerRequest.recv(BUFFSIZE)
                    print("connecton success ", msg)
                    #self.send_data("../media/image.png", "image-copy.png")
                    
                    

    def recv(self):
        self.client.setblocking(10)
        return self.client.recv(BUFFSIZE).decode(FORMAT)
    def send(self, data):
        data = str(data).encode(FORMAT)
        self.client.send(data)
    def publish():
        pass
    def fetch():
        pass
    #Config peer for using peerSock
    
    def initialize_seeding(self):
        # first make the socket start seeding 
        self.peer.start_seeding()
    def receive_data(self, fname):
        return self.peer.receive_data(fname)
    def send_data(self, lname,fname):
        return self.peer.send_data(lname,fname)
    def receive_connection(self):
        accepted_peer = self.peer.accept_connection()
        return accepted_peer
    """
        attempts to connect the peer using TCP connection 
        returns success/failure for the peer connection
    """
    def send_connection(self, ip ,port):
        # connection_log = 'SEND CONNECTION STATUS : ' + self.unique_id + ' '
        connection_status = None
        if self.peer.request_connection(ip, port):
            # user for EXCECUTION LOGGING
            # connection_log += SUCCESS
            connection_status = True
        else:
            # user for EXCECUTION LOGGING
            # connection_log += FAILURE 
            connection_status = False
         
        # self.peer_logger.log(connection_log)
        print("conection status", connection_status)
        return connection_status

    def initiate_handshake(self):
        pass
    def send_handshake(self):
        pass
    def receive_handshake(self):
        pass
    def respond_handshake(self):
        pass
        """
        disconnects the peer socket connection
    """
    def close_server_connection(self):
        self.client.close()
    def close_peer_connection(self):
        # self.state.set_null()
        self.peer.disconnect()
