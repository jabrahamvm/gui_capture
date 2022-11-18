import socket
import threading
import utils
from Camera import Camera

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8000
HEADER = 1024
FORMAT = "utf-8"
SERVER_ON = "The server is online..."
SERVER_OFF = "The server is currently offline."
SERVER_CONN = "The server has connected to AIMV"

CONECTION_ESTABLISHED = "You are now connected to the server!"

class Server():
    def __init__(self, status_variable):
        self.on = False
        self.clients = []
        self.path = ""
        self.status_variable = status_variable
        self.status_variable.set(SERVER_OFF)

    def start(self, camera, channels, host, port):
        """Initializes a server at host:port...
            - camera:
            - channels:
            - host:
            - port:
            - status_variable:
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.on = True
        self.cap = Camera(src=channels[camera.get()],resolution=(1920,1080))
        self.cap.start()
        self.status_variable.set(SERVER_ON)

        while True:
            try:
                client, addr = self.server.accept()
                #print("YES 1")
                client.send(CONECTION_ESTABLISHED.encode(FORMAT))
                #print("YES 2")
                self.clients.append((client,addr))
                #print("YES 3")
                thread = threading.Thread(name="Handling cliente thread",target=self.handle_client,args=(client, addr))
                thread.start()
                #print("YES 4")
            except:
                print(f"[SERVER CLOSED] The sever has been closed...")
                self.close()
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
        connected = True
        self.status_variable.set(SERVER_CONN)
        while connected:
            try:
                msg = client.recv(HEADER).decode(FORMAT)
                print(msg)
                if msg == "Capture\r\n":
                    utils.capture_image(cap=self.cap, path=self.path)
                else:
                    utils.capture_image(cap=self.cap, path=self.path)
                    
            except:
                client.close()
                self.clients.clear()
                self.status_variable.set(SERVER_ON)
                connected = False

    def connected(self):
        return len(self.clients) > 0
    
    def close(self):
        """ 
            Closes the server and its connections.
        """
        #print("NOOO")
        self.cap.stop()
        self.on = False
        if len(self.clients) != 0:
            for client in self.clients:
                client[0].close()
            self.clients.clear()
        self.server.close()
        self.status_variable.set(SERVER_OFF)
        #print(f"[CLOSING SERVER] Server has been closed...")
    
    def set_image_path(self, path):
        self.path = path
