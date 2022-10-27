from http import server
import tkinter as tk
from tkinter import OFF, ON, ttk
from tkinter import filedialog
import utils
import threading
import cv2
from server import Server

SERVER_OFF = "The server is off..."
SERVER_ON = "The server is listening at "
SERVER_CONNECTED = " has connected to the server, waiting for commands..."

class Application(tk.Tk):
    def __init__(self):
        """ Initializes our application"""
        super().__init__()
        self.selected_cam = tk.StringVar()
        self.channels = utils.find_cameras()
        self.HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        self.PORT = 8000         # Port to listen on (non-privileged ports are > 1023)
        self.image_path = tk.StringVar()
        self.server = Server(self.HOST,self.PORT)
        self.server_on = False
        self.server_status_text = tk.StringVar()
        self.geometry("400x400")
        self.resizable(False, False)
        self.title('Webcam test')
        self.create_widgets()

    def image_widgets(self):
        image_frame = tk.Frame(self,width=200, height=200,bg="blue")
        image_frame.pack(fill=tk.BOTH, padx=10,pady=10)

        # Combobox label
        cb_frame = tk.Frame(image_frame, width=200)
        cb_frame.pack(fill=tk.BOTH, padx=5,pady=3)
        cb_label = ttk.Label(cb_frame,text="Please select a webcam:")
        cb_label.pack(padx=5, pady=5,side=tk.LEFT)
        # Combobox displaying available cameras
        cam_cb = ttk.Combobox(cb_frame, textvariable=self.selected_cam)
        cam_cb.pack(fill=tk.X,padx=5, pady=5,side=tk.LEFT, expand=True)
        # get values for the combobox
        cam_cb['values'] = list(self.channels.keys())

        # prevent typing a value
        cam_cb['state'] = 'readonly'

        # Preview button that displays the selected camera.
        preview_btn = ttk.Button(image_frame, text="Preview selected camera", command=self.show_preview)
        preview_btn.pack(padx=1,pady=5,ipadx=3, ipady=3,expand=True,fill=tk.X)

        aux_frame = tk.Frame(image_frame,width=200)
        aux_frame.pack(fill=tk.X)
        dp_label = tk.Label(aux_frame,text="Please select a folder path to save the image:")
        dp_label.pack(fill=tk.X, expand=True, padx=5)
        # Button to select where you want to save the image
        ib_frame = tk.Frame(image_frame, width=200)
        ib_frame.pack(padx=5,pady=3)
        browse_btn = ttk.Button(ib_frame,text='Browse folder', command=self.set_directory)
        browse_btn.pack(padx=10,pady=2,ipadx=5, ipady=3)
        ip_label = tk.Label(ib_frame,textvariable=self.image_path)
        ip_label.pack(fill=tk.X)

    def server_widgets(self):
        # Create a frame that contains all the elements
        server_frame = tk.Frame(self,width=200, height=200)
        server_frame.pack(fill=tk.BOTH, padx=10,pady=10)
        # Upper frame
        # - Containes Host, port (both on sopt_f, port on port_frame) and the button to start the server.
        upper_f = tk.Frame(server_frame,width=200, height=100)
        upper_f.pack(padx=5,pady=5,fill=tk.X)
        sopt_f = tk.Frame(upper_f, width=150,height=100,bg="red")
        sopt_f.pack(side=tk.LEFT,fill=tk.BOTH)

        # Host label, host will remain constant
        host_label = ttk.Label(sopt_f,text=f"HOST:\t{self.HOST}")
        host_label.pack(fill=tk.X, padx=5, pady=5)

        # Port label and entry, by default it is set to 8000
        port_frame = tk.Frame(sopt_f,bg="yellow")
        port_frame.pack(padx=5, pady=5,fill=tk.BOTH)
        port_label = ttk.Label(port_frame,text="PORT:")
        port_label.pack(padx=5,side=tk.LEFT)
        port_entry = ttk.Entry(port_frame)
        port_entry.insert(0,str(self.PORT))
        port_entry.pack(side=tk.LEFT)

        # Start server button
        start_server_button = ttk.Button(upper_f, text="Start Server", command=self.start_server)
        start_server_button.pack(padx=(50,0),ipadx=5, ipady=5, expand=True,side=tk.LEFT,fill=tk.X)
        # Stop server button
        stop_server_button = ttk.Button(server_frame, text="Stop server", command=self.stop_server)
        stop_server_button.pack(padx=(50,0),ipadx=5, ipady=5, expand=True,fill=tk.X)

        # Separator
        separator = ttk.Separator(server_frame,orient="horizontal")
        separator.pack(fill=tk.X)

        # Server status labels
        server_status_f = tk.Frame(server_frame,width=200, height=100)
        server_status_f.pack(padx=5,pady=5,fill=tk.X)
        ss_cl = tk.Label(server_status_f,text="[SERVER STATUS]:")
        ss_cl.pack(fill=tk.X,side=tk.LEFT)
        self.server_status_text.set(SERVER_OFF)
        server_status_label = tk.Label(server_status_f,textvariable=self.server_status_text)
        server_status_label.pack(fill=tk.X,side=tk.LEFT)


    def set_directory(self):
        self.image_path.set(filedialog.askdirectory())
        self.server.set_image_path(self.image_path.get() + "/")

    def create_widgets(self):
        self.image_widgets()
        ttk.Separator(self,orient="horizontal").pack(fill=tk.X,padx=5)
        self.server_widgets()

    # bind the selected value changes
    def show_preview(self):
        """ handle the cam changed event """
        if self.selected_cam.get() == "":
            return
        cap = cv2.VideoCapture(self.channels[self.selected_cam.get()])
        utils.show_frames(cap)

    def start_server(self):
        thread = threading.Thread(target=self.server.start,args=(self.selected_cam,self.channels))
        thread.start()
        self.server_on = True
        self.server_status_text.set(SERVER_ON)

    def stop_server(self):
        self.server_on = False
        self.server.close()
        self.server_status_text.set(SERVER_OFF)