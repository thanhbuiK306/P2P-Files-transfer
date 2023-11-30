from math import ceil
import socket
import threading
import pickle
import os
import tqdm

import logging

PEERS_DIR = 'local/'
PEER_TIMEOUT = 2
FORMAT = 'utf-8'
BUFFSIZE = 2048
class file:
    chunk_size = 2048

    def __init__(self, filename: str,lname = None, owner = None):
        self.filename = filename
        if not owner:
            self.path = lname # mark as completeFile
        else:
            self.path = PEERS_DIR + filename

class completeFile(file):

    def __init__(self, filename: str, lname: str, owner= None):
        super().__init__(filename, lname, owner)
        self.size = self.get_size(self.path)
        self.n_chunks = ceil(self.size / self.chunk_size)
        self.fp = open(self.path, 'rb')

    def get_chunk_no(self, chunk_no):
        return self._get_chunk(chunk_no * self.chunk_size)

    def _get_chunk(self, offset):
        self.fp.seek(offset, 0)
        chunk = self.fp.read(self.chunk_size)
        return chunk

    @staticmethod
    def get_size(path):
        return os.path.getsize(path)

class incompleteFile(file):
    def __init__(self, filename,size,owner= None, lname = None):
        super().__init__(filename, lname,owner)
        self.size = size
        self.n_chunks = ceil(self.size / self.chunk_size)
        self.needed_chunks = [i for i in range(self.n_chunks)]
        self.received_chunks = {}
        self.fp = open(self.path, 'wb')

    def get_needed(self):
        self.needed_chunks = []
        for i in range(self.n_chunks):
            if i not in self.received_chunks:
                self.needed_chunks.append(i)
        return self.needed_chunks

    def write_chunk(self, buf, chunk_no):
        self.received_chunks[chunk_no] = buf

    def write_file(self):
        if len(self.get_needed()) == 0:
            with open(self.path, 'wb') as filep:
                for i in range(self.n_chunks):
                    filep.write(self.received_chunks[i])

def command_executor(port_no, name, p):
    connected = 0
    try:
        while True:
            inp = input(">")
            if inp == 'cls' or inp == '0':
                if connected:
                    p.disconnect()
                    del p
                    connected = 0
                else:
                    print("peer is not connected!")

            if inp == "conn" or inp == '1':
                if not connected:
                    p = start_peer(port_no, name)
                    connected = 1
                else:
                    print("peer is already connected to manager")

            if inp == "get_files":
                p.listFileAvailable()
            
            if inp == "get_peers" or inp == '2':
                update_peers_thread = threading.Thread(target=p.update_peers)
                update_peers_thread.start()
                update_peers_thread.join()
                print(f"available peers are: {p.peers}")

            if inp == "fetch" or inp == '3':
                file_name = input("Enter file name : ")
                command = "fetch "+ file_name
                p.fetch(command)

                #p.receive_file(file_name , fileOwner)

            if inp == 'shareble_files' or inp == '4':
                print(f"our available files are: {list(p.available_files.keys())}")
            if inp == 'publish':
                req_file_name = input("Input req_file_name")
                lname = input("Input lname")
                p.filePublish(req_file_name,lname)
                command = inp + " " + req_file_name +" "+lname + " "+ p.name
                p.publish(command)
            if inp == 'end' or inp == '5':
                os._exit(0)
    except KeyboardInterrupt:
        os._exit(0)
class Peer:
    s: socket.socket
    
    peers: list[(str, int)]  # list of all peers
    
    peers_connections: dict[(str, int), socket.socket]
    
    port: int
    manager_port = 1233
    addr: (str, int)
    available_files: dict[str, completeFile]

    def __init__(self, port_no: int, name: str, ip_addr='127.0.0.1'):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port_no
        self.name = name
        self.directory = PEERS_DIR + name + '/'

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        self.available_files = {}

        self.s = socket.socket()

        self.addr = (self.ip, port_no)
        self.peers_connections = {}
        self.my_socket = socket.socket()
        self.my_socket.bind((self.ip, port_no))
        
    def connect_manager(self):
        """
        connect to manager
        """
        self.s.connect(('localhost', self.manager_port))
        msg = self.s.recv(512).decode()
        if msg == 'Send port':
            self.s.send(pickle.dumps(self.addr))
    def send_manager(self,msg):
        self.s.send(msg.encode(FORMAT))
    def receive(self, port_no, name, p):
        """
        receive the other peers and update the list.
        """
        while True:
            try:
                msg = self.s.recv(512)
                msg = pickle.loads(msg)
                
                if msg == "testing conn":
                    print(msg)
                    # self.peers = msg['peers']
                    # logging.info(f"available peers are {self.peers}")
                    # print(f"available peers are {self.peers}")
                    # msg =pickle.loads(self.s.recv(512))
                    # print(msg)
                    t1 =threading.Thread(target = command_executor, args=(port_no,name,p))
                    t1.start()
                    t1.join()
                    
            except ConnectionAbortedError:
                print("connection with manager is closed")
                break

    def update_peers(self):
        try:
            msg = b"get_peers"
            self.s.send(msg)
        except Exception:
            print("could not get the peers list")
    def filePublish(self, req_file_name, lname):
        self.available_files[req_file_name] = completeFile(filename=req_file_name, lname=lname)
    def publish(self, command):
        try:
            self.s.send(command.encode(FORMAT))
            # command[0] : publish
            # command[1] : req_file_name
            # command[2] : lname 
        except Exception as e:
            print(e)
            print("could not publish the file")
    def fetch(self,command):
        self.send_manager(command)
        fileDetail = pickle.loads(self.s.recv(4096))
        print(type(fileDetail))
        print(fileDetail)
        # connect
        ownerIp = fileDetail[0]
        ownerPort= int(fileDetail[1])
        ownerName = fileDetail[2]
        ownerreq_file_name = fileDetail[3]
        self.receive_file((ownerIp, ownerPort),ownerName, ownerreq_file_name)
        # rec file
    # def __del__(self):
    #     self.s.close()
    #     self.my_socket.close()
    def listFileAvailable(self):
        self.send_manager("get_files")
        data= self.s.recv(4096)
        listFile = pickle.loads(data)
        print(listFile)
    def disconnect(self):
        """
        Disconnect the connected socket.
        """
        self.s.send(b"close")
        self.s.close()
        self.my_socket.close()

    def connect_to_peers(self):
        """
        Listens to other peers and adds into peer connections
        """

        self.my_socket.listen(10)
        try:
            while True:
                c, addr = self.my_socket.accept()
                print(addr)
                self.peers_connections[addr] = {
                    "connection": c
                }
                #self.listen_to_peer(c, addr)
                # print(threading.active_count())
                listen_peers_thread = threading.Thread(target=self.listen_to_peer, args=(c, addr))
                listen_peers_thread.start()
                listen_peers_thread.join()
        except OSError as e:
            print(e.errno)

    def listen_to_peer(self, c: socket.socket, addr):
        """
        Listen to peer and give response when asked.
        """
        
        while True:
            try:
                # handle when peer disconnect
                msg = pickle.loads(c.recv(2048))

                if msg['type'] == 'fetch':
                    req_file_name = msg['data']
                    if req_file_name in self.available_files:
                        file_detail = pickle.dumps({
                            "type": "available_file",
                            "data": {
                                "filesize": str(self.available_files[req_file_name].size)
                            }
                        })
                        c.send(file_detail)
                        with self.available_files[req_file_name].fp as f:
                            data_sent = 0
                            file_size = self.available_files[req_file_name].size
                            progress = tqdm.tqdm(range(file_size), desc=req_file_name, unit='B', unit_scale=True, unit_divisor=BUFFSIZE)
                            while data_sent < file_size:
                                file_data = f.read(BUFFSIZE)
                                c.sendall(file_data)
                                data_sent += BUFFSIZE
                                progress.update(BUFFSIZE)
                            progress.desc = f'{req_file_name} Sent'
                            progress.close()
                            print("send successful")
                if msg['type'] == 'request_chunk':
                    file_name = msg['data']['filename']
                    chunk_no = msg['data']['chunk_no']
                    chunk = self.available_files[file_name].get_chunk_no(chunk_no)
                    ret_msg = pickle.dumps({
                        "type": "response_chunk",
                        "data": {
                            "chunk_no": chunk_no,
                            "filename": file_name,
                            "chunk": chunk
                        }
                    })

                    c.send(ret_msg)
            except EOFError:  # TODO: don't know what is happening here.
                pass

    def connect_to_peer(self, addr):
        """
        Connect to the peer through new and return the connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            print("Connectted to ", addr)
            logging.info(f"Connected to Peer {addr}")
        except:
            print("could not connect to ", addr)
        return sock

    def connect_and_fetch_file_detail(self, addr, file_name, file_detail: dict[str, object]):
        c = self.connect_to_peer(addr) #addr retrive from server
        msg = pickle.dumps({
            "type": "fetch",
            "data": file_name
        })
        c.send(msg)
        c.settimeout(10000)

        try:
            msg = pickle.loads(c.recv(4096)) # error here
            if msg['type'] == "available_file":
                file_detail['size'] = msg['data']['filesize']
                file_detail['peer_own_file'] = addr
                print("i need more sleep", file_detail)
                
                file_data = b''
                file_size = int(file_detail['size'])
                progress = tqdm.tqdm(range(file_size), desc=f"Receiving {file_name}", unit='B', unit_scale=True, unit_divisor=2048)
                while len(file_data) < file_size:
                    data = c.recv(BUFFSIZE)
                    file_data += data
                    progress.update(BUFFSIZE)
                progress.desc = f"{file_name} Received"
                progress.close()

                file_path = os.path.join('local/', file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                print("fetch successful")
        except socket.timeout:
            print("socket did not respond while fetching detail of file")
        c.close()

    def get_file_detail(self,p, file_name: str):
        """
        Check which peers have the file and what parts of it they have.
        Details of the file such as size are also sent.
        """
        file_detail = {
            "size": None,
            "peer_own_file": None #(str,int)
        }
        # p = fetchFileFrom
        if p != self.addr:
            print(p, self.addr)
            self.connect_and_fetch_file_detail(p, file_name, file_detail)
        return file_detail

    def get_chunk_from_peer(self, filename, peer_addr, chunk_no, incomp_file: incompleteFile):
        c = self.connect_to_peer(peer_addr)
        msg = pickle.dumps({
            "type": "request_chunk",
            "data": {
                "filename": filename,
                "chunk_no": chunk_no
            }
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        try:
            msg = pickle.loads(c.recv(4096))

            if msg['type'] == "response_chunk":
                incomp_file.write_chunk(msg['data']['chunk'], chunk_no)

        except socket.timeout:
            print(f"peer {peer_addr} did not send the file")

        logging.info(f"received the chunk {chunk_no}/{incomp_file.n_chunks} from {peer_addr}")
        print(f"received the chunk {chunk_no}/{incomp_file.n_chunks} from {peer_addr}")

        c.close()

    def receive_file(self, peerAddr, fileOwner, filename):
        file_detail = self.get_file_detail(peerAddr ,filename)
        logging.info(f"{file_detail}")
        if file_detail['size'] is None:
            print("File not found")
            return
        # recieving_file = incompleteFile(filename=filename, owner = self.name, size= int(file_detail['size']))
        
        # print(recieving_file)
        # while len(recieving_file.get_needed()) != 0:
        #     self.update_peers()
        #     peer_own_file = self.get_file_detail(peerAddr,filename)['peer_own_file']
        #     if peer_own_file == None:
        #         print(f"there are no peers with file {filename}")
        #         del recieving_file
        #         return

        #     needed_chunks = recieving_file.get_needed()
        #     print(needed_chunks)
        #     print(peer_own_file)

        # recieving_file.write_file()
        # self.available_files[filename] = completeFile(filename=filename, owner = self.name)
        # print(f"recieved {filename}")


def start_peer(port_no, name):
    """
    start the peer.
    """
    p = Peer(port_no, name)
    p.connect_manager()
    receive_thread = threading.Thread(target=p.receive, args =(port_no,name,p, ))
    receive_thread.start()
    connect_peers_thread = threading.Thread(target=p.connect_to_peers)
    connect_peers_thread.start()
    receive_thread.join()
    connect_peers_thread.join()

    return p
if __name__ == "__main__":
    port_no = int(input("Enter Port Number: "))
    name = input("Enter your name: ")
    #logging.basicConfig(filename="logs/" + name + '.log', encoding='utf-8', level=logging.DEBUG)
    try: 
        p = start_peer(port_no, name)
        connected = 1
        print("peer is already connected to manager")
        print("========================================")
        print("Give one of the commands:")
        print("0|cls: Close the connection with manager")
        print("2|get_peers: update the peers list")
        print("3|get_files: get files from peers")
        print("4|sharable_files: get the list of sharable files")
        print("5|publish: publish file")
        print("6|end: End the program\n\n")
    except:
        print("Connection Failed")
        
        