import socket
import os 
import tqdm
import argparse
import threading 
from server import on_new_conn 


HEADER = 64
FORMAT = 'utf-8'
mstsocket = socket.socket()
mstsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def readyToServe():
    while True:
        try: 
            conn, addr = mstsocket.accept()
            threading._start_new_thread(on_new_conn,(conn, addr))
            message = str("Server ready to serve...").encode(FORMAT)
            conn.send(message)
        except KeyboardInterrupt:
            print(f"Gracefully shutting down the server!")
        except Exception as e:
            print(f"Well I did not anticipate this: {e}")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "This is the server for the multithreaded socket demo!")
    parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
    parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 5000)
    args = parser.parse_args()

    print(f"Running the server on: {args.host} and port: {args.port}")
    
    try: 
        mstsocket.bind((args.host, args.port))
        mstsocket.listen(5)
    except Exception as e:
        raise SystemExit(f"We could not bind the server on host: {args.host} to port: {args.port}, because: {e}")
    
    readyToServe()