import threading
import time 

def server_command_executor():
    print("Server side... ")
    while True:
        command  = input()
        command = command.split(' ')
        time.sleep(1)        
        if command[0] == 'discover':
            print("[DISCOVER] hostname")
        elif command[0] == 'ping':
            print("[PING] hostname")
        elif command[0] =='exit':
            print("[EXIT] successfull, all connetion has been closed")
            break
        else:
            print("[INCOMPLETE] command not found")

def client_command_executor():
    print("Client side... ")
    # command = command.split(' ')  
    while True:
        command = ['publish']
        time.sleep(1) 
        if command[0] == 'publish':
            print("[FETCHING] successful")
            
        elif command[0] == 'fetch':
            print("[FETCHING]Server ready to be provide communication...")
        elif command[0]== 'exit':
            print("[EXIT] successful")
            break
        else:
            print("[INCOMPLETE]Command incorrectly, please input another statement...")
            
if __name__ =='__main__':
    threading.Thread(target= server_command_executor, daemon= True).start()
    threading.Thread(target=client_command_executor, daemon= True).start()