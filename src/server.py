import socket
import threading
import utils
from Camera import Camera

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8000
HEADER = 1024
FORMAT = "utf-8"
SERVER_ON = "The server is ONLINE"
SERVER_OFF = "The server is OFFLINE."
SERVER_CONN = "The server has CONNECTED to AIMV"

CONECTION_ESTABLISHED = "You are now connected to the server!"

class Server():
    def __init__(self, status_displays):
        self.on = False
        self.clients = []
        self.path = ""
        self.status_variable = status_displays[0]
        self.status_variable.set(SERVER_OFF)
        self.exceptions_variable = status_displays[1]
        self.exceptions_variable.set("")

    def start(self, camera, channels, host, port):
        """Initializes a server at host:port...
            - camera:
            - channels:
            - host:
            - port:
            - status_variable:
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            #self.exceptions_variable.set(f"Error creating socket: {e}")
            print(e)

        try:
            self.server.bind((host, port))
        except socket.gaierror as e:
            #self.exceptions_variable.set(f"Error with port: {e}")
            print(e)
        except socket.error as e:
            #self.exceptions_variable.set(f"Connection error: {e}")
            print(e)

        self.server.listen()
        self.on = True
        self.cap = Camera(src=channels[camera.get()],resolution=(1920,1080))
        self.cap.start()
        self.status_variable.set(SERVER_ON)

        while True:
            try:
                client, addr = self.server.accept()
                self.clients.append((client,addr))
                thread = threading.Thread(name="Handling cliente thread",target=self.handle_client,args=(client, addr))
                thread.start()
            except:
                #print(f"[SERVER CLOSED] The sever has been closed...")
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
                #print(msg)
                if msg == "Capture\r\n":
                    utils.capture_image(cap=self.cap, path=self.path)       
            except socket.error as e:
                if not self.on:
                    return
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
        if not self.on:
            return
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
