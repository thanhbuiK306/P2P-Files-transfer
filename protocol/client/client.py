def command_executor(self, self):
        connected = 0
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

                if inp == "conn" or inp == '1':
                    if not connected:
                        self.start_peer(self.port_no, self.name)
                        connected = 1
                    else:
                        print("peer is already connected to manager")

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
                    print(file)
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