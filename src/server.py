from ast import arg
import socket
import threading
import cv2
import utils
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8000
HEADER = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT\r\n"
CONECTION_ESTABLISHED = "You are now connected to the server!"

class Server():
    def __init__(self, host = HOST, port = PORT):
        self.host = host
        self.port = port
        self.connections = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, camera, channels):
        self.server.bind((self.host, self.port))
        self.server.listen()
        while True:
            print(f"[LISTENING] Server is listening on {(self.host,self.port)}")
            client, addr = self.server.accept()
            client.send(CONECTION_ESTABLISHED.encode(FORMAT))
            self.connections += 1
            thread = threading.Thread(target=self.handle_client,args=(client, addr, camera, channels))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {self.connections}")
            print("[CONNECTED CLIENTS]:", addr)

    def handle_client(self, client, addr, camera, channels):
        print(f"[NEW CONNECTION] {str(addr)} connected.")
        connected = True
        reply = ""
        while connected:
            try:
                msg = client.recv(HEADER).decode(FORMAT)
                print(msg)
                if msg == "Capture\r\n":
                    utils.capture_image(camera=camera,channels=channels)
                    reply = "The image has been captured!"
                else:
                    reply = f"You sent {msg}"
                        
                print(f"[{addr}] {msg}")
                client.sendall(reply.encode(FORMAT))
            except:
                self.connections -= 1
                client.close()
                print(f"[{addr}] has diconnected.")
                connected = False

    def close(self):
        pass

