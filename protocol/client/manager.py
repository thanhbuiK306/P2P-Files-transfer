# creating a manager for Peer to Peer network
import socket
import threading
import time
import pickle
import os
# import numpy as np
import pandas as pd

CONN_TEST_TIME = 1
FORMAT = 'utf-8'

def is_socket_closed(sock: socket.socket) -> bool:
    """
    for a given socket see if it is closed.
    """
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        # sock.settimeout(0.5)
        try:
            obj = pickle.dumps('testing conn')
            sock.send(obj)
            sock.recv()
        except socket.error:
            return True
        return False

    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        # logger.exception("unexpected exception when checking if a socket is closed")
        return True
    return False


class Manager:
    """
    Manages the network
    """
    s: socket.socket
    connections: dict[(str, int), (socket.socket, (str, int))]
    accept_thread: threading.Thread
    broadcast_peers_thread: threading.Thread
    recv_msg_thread: threading.Thread

    server_ip = ''
    port = 1233
    connections = dict()

    df = pd.DataFrame([], columns=('ip','port', 'owner', 'fname'))
 
    print(df)
    
    def __init__(self):
        self.s = socket.socket()
        self.s.bind((self.server_ip, self.port))
        self.s.listen(10)
        print("up and running")

    def __del__(self):
        self.s.close()

    def server_command_executor(self):
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
    def accept_connections(self):
        """
        accepts connections from peers and adds them into a list

        """
        while True:
            c, addr = self.s.accept()


            c.send(b'Send port')
            c.settimeout(2)
            peer_addr = pickle.loads(c.recv(512))
            self.connections[addr] = (c, peer_addr)
            print(f"Got connection from {addr, peer_addr}")
            self.recv_msg_thread = threading.Thread(target=self.recv_msg, args=(c, peer_addr))
            self.recv_msg_thread.start()
            # self.start_broadcast_peers_thread()
            
    def send_fileDetail(self, c: socket.socket,fname):
        file_detail = self.df.where(self.df['fname'] == fname)
        # Iterate over each row 
        my_list =[]
        for index, rows in file_detail.iterrows(): 
            # Create list for the current row 
            my_list =[rows.ip, rows.port, rows.owner, rows.fname] 
        data = pickle.dumps(my_list)
        c.send(data)
    def recv_msg(self, c: socket.socket, addr: (str, int)):
        """
        revive msgs from the peers
        """
        while True:
            c.settimeout(10000)
            try:
                msg = c.recv(512).decode(FORMAT)

                if msg == 'close':
                    print(addr)
                    self.connections.pop(addr)
                    self.start_broadcast_peers_thread()
                    break

                if msg == 'get_peers':
                    conn = pickle.dumps({
                        "type": "peers",
                        "peers": [x[1] for a, x in self.connections.items()]
                    })
                    c.send(conn)
                if msg == 'get_files':
                    print(msg)
                    file_detail = self.df
                    # Iterate over each row 
                    my_list =[]
                    for index, rows in file_detail.iterrows(): 
                        # Create list for the current row 
                        my_list =[rows.ip, rows.port, rows.owner, rows.fname]
                    data = pickle.dumps(my_list)
                    c.send(data)
                if msg.split(' ')[0] == 'fetch':
                    fname = msg.split(' ')[1]
                    fileInfo_thread = threading.Thread(target = self.send_fileDetail, args =(c, fname,))
                    fileInfo_thread.start()
                if msg.split(' ')[0] == 'publish':
                    
                    command = msg.split(' ')
                    self.df.loc[len(self.df.index)] = [addr[0],addr[1],command[3], command[1]]
                    #print(self.df)
                    #send to s a pickle that contain information to connect to peer to recv file
            except Exception as e:
                print(f"got exception {e} while receiving from addr {addr}")
                break

    def periodic_conn_test(self):
        """
        see if the connected peers are reachable.
        If not, remove them from the peers list and broadcast.
        """
        while True:
            closed_connections = []  # stores the keys for closed connections
            for addr, c in self.connections.items():
                if is_socket_closed(c[0]):
                    closed_connections.append(addr)

            n_closed = len(closed_connections)
            for addr in closed_connections:
                self.connections.pop(addr)

            # if n_closed > 0:
            #     self.start_broadcast_peers_thread()

            time.sleep(CONN_TEST_TIME)

    def start_broadcast_peers_thread(self):
        """
        start the broadcast thread
        """
        self.broadcast_peers_thread = threading.Thread(target=self.broadcast_peers)
        self.broadcast_peers_thread.start()

    def broadcast_peers(self):
        """
        sends the details about peers to other peers
        """
        conn = pickle.dumps({
            "type": "peers",
            "peers": [ x[1] for a, x in self.connections.items() ]
        })
        for addr in self.connections:
            self.connections[addr][0].send(conn)

    def run(self):
        """
        run the manager
        """
        self.server_thread = threading.Thread(target=self.server_command_executor)
        self.server_thread.start()
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.start()
        self.periodic_conn_test_thread = threading.Thread(target=self.periodic_conn_test)
        self.periodic_conn_test_thread.start()
        self.server_thread.join()
        self.accept_thread.join()
        self.periodic_conn_test_thread.join()


if __name__ == "__main__":
    try:
        manager = Manager()
        manager.run()
        inp = input()
        if inp == 'c' or inp == 'close':
            os._exit(0)

    except KeyboardInterrupt:
        os._exit(0)