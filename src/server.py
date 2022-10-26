from ast import arg
from audioop import add
import socket
import threading
import cv2
import utils

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8000
HEADER = 1024
FORMAT = "utf-8"

CONECTION_ESTABLISHED = "You are now connected to the server!"

class Server():
    def __init__(self, host = HOST, port = PORT):
        self.host = host
        self.port = port
        self.on = False
        self.clients = []

    def start(self, camera, channels):
        """Initializes a server..."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.on = True
        while True:
            try:
                print(f"[LISTENING] Server is listening on {(self.host,self.port)}")
                client, addr = self.server.accept()
                client.send(CONECTION_ESTABLISHED.encode(FORMAT))
                self.clients.append((client,addr))
                print("[ACTIVE CONNECTIONS]:",[client[1] for client in self.clients])
                thread = threading.Thread(target=self.handle_client,args=(client, addr, camera, channels))
                thread.start()
            except Exception as e:
                print(f"[SERVER CLOSED] The sever has been closed... {e}")
                return


    def handle_client(self, client, addr, camera, channels):
        """Handles connections to the server, it has a blocking fucntion, so it must be called in a thread.
            - client:   Client that the server is connected to.
            - addr:     Address of the client.
            - camera:
            - channels:
        """
        print(f"[NEW CONNECTION] {str(addr)} connected.")
        connected = True
        reply = ""
        while connected:
            try:
                msg = client.recv(HEADER).decode(FORMAT)
                if msg == "Capture\r\n":
                    utils.capture_image(camera=camera,channels=channels)
                    reply = "The image has been captured!"
                else:
                    reply = f"You sent {msg}"
                        
                print(f"[{addr}] {msg}")
                client.sendall(reply.encode(FORMAT))
            except:
                client.close()
                self.clients.clear()
                print(f"[{addr}] has diconnected.")
                connected = False

    def close(self):
        """ 
            Closes the server and its connections.
        """
        self.on = False
        if len(self.clients) != 0:
            for client in self.clients:
                client[0].send("\nSERVER IS CLOSING...".encode(FORMAT))
                client[0].close()
            self.clients.clear()
        self.server.close()
        print(f"[CLOSING SERVER] Server has been closed...")

