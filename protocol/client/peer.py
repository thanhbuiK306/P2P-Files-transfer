from math import ceil
import socket
import threading
import pickle
import os
import tqdm

import logging

PEERS_DIR = 'local/'
PEER_TIMEOUT = 10
FORMAT = 'utf-8'
BUFFSIZE = 4096
class file:
    chunk_size = 4096

    def __init__(self, filename: str,lname = None, owner = None):
        self.filename = filename
        if lname:
            self.path = lname # mark as completeFile
        else:
            self.path = PEERS_DIR + filename

class completeFile(file):

    def __init__(self, filename: str, lname = None, owner= None):
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
class Peer:
    s: socket.socket
    
    peers: list[(str, int)]  # list of all peers
    
    peers_connections: dict[(str, int), socket.socket]
    
    port: int
    manager_port = 1233
    addr: (str, int)
    available_files: dict[str, completeFile]
    list_files =[]
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
        try:
            self.s.send(msg.encode(FORMAT))
        except:
            print("Server connection has been shut down")
    def receive(self, port_no, name, p):
        """
        receive the other peers and update the list.
        """
        while True:
            try:
                msg = self.s.recv(512)
                msg = pickle.loads(msg)
                if msg == "testing conn":
                    # self.peers = msg['peers']
                    # logging.info(f"available peers are {self.peers}")
                    # print(f"available peers are {self.peers}")
                    # msg =pickle.loads(self.s.recv(512))
                    # print(msg)
                    t1 =threading.Thread(target = self.command_executor)
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
    def filePublish(self, req_filename, lname):
        try:
            self.available_files[req_filename] = completeFile(filename=req_filename, lname=lname)
            return True
        except:
            print("Path does not exists")
        return False
    def publish(self, command):
        try:
            self.s.send(command.encode(FORMAT))
            # command[0] : publish
            # command[1] : req_filename
            # command[2] : lname 
        except Exception as e:
            print("could not publish the file")
    def fetch(self,command):
        self.send_manager(command)
        fileDetail = pickle.loads(self.s.recv(4096))
        # connect
        ownerIp = fileDetail[0]
        ownerPort= int(fileDetail[1])
        ownerreq_filename = fileDetail[3]
        self.receive_file((ownerIp, ownerPort),ownerreq_filename)
        # rec file
    # def __del__(self):
    #     self.s.close()
    #     self.my_socket.close()
    def listFileAvailable(self):
        self.send_manager("get_files")
        try:
            rows= self.s.recv(4096).decode(FORMAT)
            self.s.send(b'ACK')
            self.list_files = []
            for row in range(int(rows)):
                data= self.s.recv(4096)
                file = pickle.loads(data)
                file.append(row)
                self.list_files.append(file)
                self.s.send(b'ACK')
            return self.list_files
        except: 
            # print("connection with manager is closeddddd")
            os._exit(0)

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
                    req_filename = msg['data']
                    if req_filename in self.available_files:
                        file_detail = pickle.dumps({
                            "type": "available_file",
                            "data": {
                                "filesize": str(self.available_files[req_filename].size)
                            }
                        })
                        c.sendall(file_detail)

                if msg['type'] == 'request_chunk':
                    filename = msg['data']['filename']
                    chunk_no = msg['data']['chunk_no']
                    chunk = self.available_files[filename].get_chunk_no(chunk_no)
                    ret_msg = pickle.dumps({
                        "type": "response_chunk",
                        "data": {
                            "chunk_no": chunk_no,
                            "filename": filename,
                            "chunk": chunk
                        }
                    })
                    c.sendall(ret_msg)
            except EOFError:  # TODO: domn't know what is happening here.
                pass

    def connect_to_peer(self, addr):
        """
        Connect to the peer through new and return the connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            sock.setblocking(1)
            print("Connectted to ", addr)
            logging.info(f"Connected to Peer {addr}")
        except:
            print("could not connect to ", addr)
        return sock

    def connect_and_fetch_file_detail(self, addr, filename, file_detail: dict[str, object]):
        c = self.connect_to_peer(addr) #addr retrive from server
        msg = pickle.dumps({
            "type": "fetch",
            "data": filename
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)

        msg = pickle.loads(c.recv(2048)) 
        if msg['type'] == "available_file":
            file_detail['size'] = msg['data']['filesize']
            file_detail['peer_own_file'] = addr

        if file_detail['size'] is None:
            print("File not found")
            return
        try:
            recieving_file = incompleteFile(filename=filename, owner = self.name, size= int(file_detail['size']))
            needed_chunks = recieving_file.get_needed()
            peer_own_file = addr
            i =0
            progress = tqdm.tqdm(range(len(needed_chunks)), desc=f"Receiving {filename}")
            if  len(recieving_file.get_needed()) != 0:       
                while i < len(needed_chunks):
                        msg = pickle.dumps({
                            "type": "request_chunk",
                            "data": {
                                "filename": filename,
                                "chunk_no": i
                            }
                        })
                        c.send(msg)
                        c.settimeout(10000)            
                        try:
                            data = c.recv(8192)
                            msg = pickle.loads(data) 
                            if msg['type'] == "response_chunk":
                                recieving_file.write_chunk(msg['data']['chunk'], i)
                                progress.update(1)

                        except socket.timeout:
                            print(f"peer {peer_own_file} did not send the file")

                        logging.info(f"received the chunk {i}/{recieving_file.n_chunks} from {peer_own_file}")
                        i += 1
                progress.desc = f"{filename} Received"
                progress.close()
                recieving_file.write_file()
                self.available_files[filename] = completeFile(filename=filename, owner = self.name)
                # print("fetch successful")
        except socket.timeout:
            print("socket did not respond while fetching detail of file")
        c.close()

    def get_file_detail(self,p, filename: str):
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
            self.connect_and_fetch_file_detail(p, filename, file_detail)
        return file_detail

    def get_chunk_from_peer(self, filename, peer_addr, chunk_no, incomp_file: incompleteFile, c: socket.socket): # how connect have execute in connect_and_fetch_file_detail
        # c = self.connect_to_peer(peer_addr)
        msg = pickle.dumps({
            "type": "request_chunk",
            "data": {
                "filename": filename,
                "chunk_no": chunk_no
            }
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        
        msg = pickle.loads(c.recv(2048))
        try:
            if msg['type'] == "response_chunk":
                incomp_file.write_chunk(msg['data']['chunk'], chunk_no)

        except socket.timeout:
            print(f"peer {peer_addr} did not send the file")

        logging.info(f"received the chunk {chunk_no}/{incomp_file.n_chunks} from {peer_addr}")
        # print(f"received the chunk {chunk_no}/{incomp_file.n_chunks} from {peer_addr}")


    def receive_file(self, peerAddr, filename):
        self.get_file_detail(peerAddr ,filename)
        # logging.info(f"{file_detail}")
        # if file_detail['size'] is None:
        #     print("File not found")
        #     return
        # recieving_file = incompleteFile(filename=filename, owner = self.name, size= int(file_detail['size']))
        

        # i = 0
        # running_threads = []
        # peer_own_file = file_detail['peer_own_file'] # check peer online needed!!!!!
        # if peer_own_file == None:
        #     print(f"there are no peers with file {filename}")
        #     del recieving_file
        #     return
        # needed_chunks = recieving_file.get_needed()
        # while len(recieving_file.get_needed()) != 0:       
        #     print(i)
        #     if i < len(needed_chunks):
        #         get_chunk_thread = threading.Thread(
        #             target=self.get_chunk_from_peer,
        #             args=(filename, peer_own_file, needed_chunks[i], recieving_file)
        #         )
        #         running_threads.append(get_chunk_thread)
        #         get_chunk_thread.start()
        #         i += 1
        #         get_chunk_thread.join()

        # recieving_file.write_file()
        # self.available_files[filename] = completeFile(filename=filename, owner = self.name)
        # print(f"recieved {filename}")

    def command_executor(self):
        connected = 1
        try:
            while True:
                inp = input(">")
                if inp == 'cls' or inp == '0':
                    if connected:
                        self.disconnect()
                        del self.s
                        connected = 0
                    else:
                        print("peer is not connected!")

                if inp == "get_files":
                    print(self.listFileAvailable())
                
                if inp == "get_peers" or inp == '2':
                    update_peers_thread = threading.Thread(target=self.update_peers)
                    update_peers_thread.start()
                    update_peers_thread.join()
                    print(f"available peers are: {self.peers}")

                if inp == "fetch" or inp == '3':
                    listFile = self.listFileAvailable()
                    for file in listFile:
                        print(f"File {file[3]} was published by {file[2]}")
                    file = listFile[int(input("Choose your file you want"))]
                    command = "fetch "+ file[3] + " " + file[2]
                    self.fetch(command)

                    #self.receive_file(filename , fileOwner)

                if inp == 'shareble_files' or inp == '4':
                    print(f"our available files are: {list(self.available_files.keys())}")
                if inp == 'publish':
                    req_filename = input("Input req_filename")
                    lname = input("Input lname")
                    while not self.filePublish(req_filename,lname) :
                        lname = input("Input lname again")
                    command = inp + " " + req_filename +" "+lname + " "+ self.name
                    self.publish(command)
                if inp == 'end' or inp == '5':
                    os._exit(0)
        except KeyboardInterrupt:
            os._exit(0)
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
        
        