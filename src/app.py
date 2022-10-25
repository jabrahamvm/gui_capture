import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import utils
import threading
import cv2
from server import Server

class Application(tk.Tk):
    def __init__(self):
        """ Initializes our our application"""
        super().__init__()
        self.selected_cam = tk.StringVar()
        self.channels = utils.find_cameras()
        self.HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        self.PORT = 8000 # Port to listen on (non-privileged ports are > 1023)
        self.image_path = ""
        self.server = Server(self.HOST,self.PORT)
        self.geometry("400x400")
        self.resizable(False, False)
        self.title('Webcam test')
        self.create_widgets()

    def create_widgets(self):
        # Combobox label
        cb_label = ttk.Label(text="Please select a webcam:")
        cb_label.pack(fill=tk.X, padx=5, pady=5)
        # Combobox displaying available cameras
        cam_cb = ttk.Combobox(self, textvariable=self.selected_cam)
        cam_cb.place(x=24, y=50)
        cam_cb.configure(width=55)
        cb_label.place(x=24, y=27)
        # get values for the combobox
        cam_cb['values'] = list(self.channels.keys())

        # prevent typing a value
        cam_cb['state'] = 'readonly'

        # Button to select where you want to save the image
        browse_btn = ttk.Button(text='Browse folder', command=lambda : filedialog.askdirectory())
        browse_btn.pack(ipadx=5, ipady=5, expand=True)
        browse_btn.place(x=111, y=88)

        # Preview button that displays the selected camera.
        preview_btn = ttk.Button(self, text="Preview", command=self.show_preview)
        preview_btn.pack(ipadx=5, ipady=5, expand=True)
        preview_btn.place(x=220, y=88)

        # Preview button that displays the selected camera.
        start_server_button = ttk.Button(self, text="Start Server", command=self.start_server)
        start_server_button.pack(ipadx=5, ipady=5, expand=True)


    def save_image(self):
        if self.selected_cam.get() == "":
            return
        cap_tmp = cv2.VideoCapture(self.channels[self.selected_cam.get()])
        _, frame = cap_tmp.read()
        cv2.imwrite("image.jpg", frame)
        # When everything done, release the capture
        cap_tmp.release()

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

    def stop_server(self):
        self.server.close()