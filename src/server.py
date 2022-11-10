import socket
import threading
import utils
import cv2
import time
from imutils import WebcamVideoStream

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8000
HEADER = 1024
FORMAT = "utf-8"

CONECTION_ESTABLISHED = "You are now connected to the server!"

class Server():
    def __init__(self):
        self.on = False
        self.clients = []
        self.path = ""

    def start(self, camera, channels, host, port, status_variable):
        """Initializes a server at host:port...
            - camera:
            - channels:
            - host:
            - port:
            - status_variable:
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cap = cv2.VideoCapture(channels[camera.get()], cv2.CAP_DSHOW)
        self.server.bind((host, port))
        self.server.listen()
        self.on = True
        while True:
            try:
                print(f"[LISTENING] Server is listening on {(host,port)}")
                client, addr = self.server.accept()
                client.send(CONECTION_ESTABLISHED.encode(FORMAT))
                self.clients.append((client,addr))
                status_variable.set(f"The server has connected to AIMV")
                print("[ACTIVE CONNECTIONS]:",[client[1] for client in self.clients])
                thread = threading.Thread(target=self.handle_client,args=(client, addr))
                thread.start()
            except:
                print(f"[SERVER CLOSED] The sever has been closed...")
                return

    def server_on(self):
        return self.on

    def handle_client(self, client, addr):
        """Handles connections to the server, it has a blocking fucntion, so it must be called in a thread.
            - client:   Client that the server is connected to.
            - addr:     Address of the client.
            - camera:
            - channels:
        """
        print(f"[NEW CONNECTION] {str(addr)} connected.")
        connected = True
        while connected:
            try:
                msg = client.recv(HEADER).decode(FORMAT)
                if msg == "Capture\r\n":
                    start = time.time()
                    utils.capture_image(cap=self.cap, path=self.path)
                    end = time.time()
                    print(f"The picture has taken {end - start} seconds...")
                    print(f"[{addr}] {msg}")
            except:
                client.close()
                self.clients.clear()
                print(f"[{addr}] has diconnected.")
                connected = False

    def connected(self):
        return len(self.clients) > 0
    
    def close(self):
        """ 
            Closes the server and its connections.
        """
        self.cap.release()
        self.on = False
        if len(self.clients) != 0:
            for client in self.clients:
                client[0].close()
            self.clients.clear()
        self.server.close()
        print(f"[CLOSING SERVER] Server has been closed...")
    
    def set_image_path(self, path):
        self.path = path
