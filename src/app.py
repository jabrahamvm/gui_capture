import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import utils
import threading
from server import Server


class Application(tk.Tk):
    """
        Application that uses acts as a Server and waits for requests to take pictures with a 
        selected camera device.
    """
    def __init__(self):
        """ Initializes our application"""
        super().__init__()
        # Variables to control camera selection
        self.selected_cam = tk.StringVar()
        self.channels = utils.find_cameras()
        # Standard loopback interface address (localhost)
        self.HOST = "127.0.0.1"
        # Port to listen on (non-privileged ports are > 1023)
        self.PORT = tk.StringVar()
        self.PORT.set("8000") 
        self.PORT.trace("w", lambda *args: None)

        self.server_status_text = tk.StringVar()
        self.server_status_text.trace("w",lambda *args : None)
        self.server_exceptions_text = tk.StringVar()
        self.server_exceptions_text.trace("w",lambda *args : None)

        self.server = Server(status_displays=(self.server_status_text, self.server_exceptions_text))
        self.server_on = False

        # Image path variable for the label
        self.image_path = tk.StringVar()
        # Tkinter default configurations
        self.geometry("400x400")
        self.resizable(False, False)
        self.title('AIMV Microscope Server')
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def image_widgets(self):
        """ Handles the initialization of all the image-related widgets. """
        image_frame = tk.Frame(self,width=200, height=200)
        image_frame.pack(fill=tk.BOTH, padx=10,pady=10)

        # Combobox label
        cb_frame = tk.Frame(image_frame, width=200)
        cb_frame.pack(fill=tk.BOTH, padx=5,pady=3)
        cb_label = ttk.Label(cb_frame,text="Please select a camera:")
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
        dp_label = tk.Label(aux_frame,text="Please select a folder path to save the image:",anchor="w",justify=tk.LEFT)
        dp_label.pack(fill=tk.X, expand=True, padx=5)
        # Button to select where you want to save the image
        ib_frame = tk.Frame(image_frame, width=200)
        ib_frame.pack(padx=5,pady=3,fill=tk.X,expand=True)
        browse_btn = ttk.Button(ib_frame,text='Browse folder', command=self.set_directory)
        browse_btn.pack(pady=2,ipadx=5, ipady=3,side=tk.LEFT)
        ipath_entry = ttk.Entry(ib_frame,textvariable=self.image_path)
        ipath_entry.pack(side=tk.RIGHT,ipadx=5, ipady=5, pady=5,padx=5,fill=tk.X, expand=True)
        ipath_entry.config(state="disabled")

    def server_widgets(self):
        """ Handles the initialization of all the server-related widgets. """
        # Create a frame that contains all the elements
        server_frame = tk.Frame(self,width=200, height=200)
        server_frame.pack(fill=tk.BOTH, padx=10,pady=10)
        # Upper frame
        # - Containes Host, port (both on sopt_f, port on port_frame) and the button to start the server.
        upper_f = tk.Frame(server_frame,width=200, height=100)
        upper_f.pack(padx=5,pady=5,fill=tk.BOTH)

        tk.Label(upper_f,text="Server Options",anchor="w",justify=tk.LEFT).pack(expand=True,fill=tk.X)
        ttk.Separator(upper_f,orient="horizontal").pack(fill=tk.X)

        sopt_f = tk.Frame(upper_f, width=150,height=100)
        sopt_f.pack(side=tk.LEFT,fill=tk.BOTH)

        # Host label, host will remain constant
        host_label = ttk.Label(sopt_f,text=f"HOST:\t{self.HOST}")
        host_label.pack(fill=tk.BOTH, padx=5, pady=5,ipadx=5, ipady=5)

        # Port label and entry, by default it is set to 8000
        port_frame = tk.Frame(sopt_f)
        port_frame.pack(fill=tk.BOTH)
        port_label = ttk.Label(port_frame,text="PORT:")
        port_label.pack(padx=5,pady=5,ipadx=5, ipady=5,side=tk.LEFT)
        port_entry = ttk.Entry(port_frame,textvariable=self.PORT)
        port_entry.pack(side=tk.LEFT,ipadx=5, ipady=5,padx=5, pady=5)

        buttons_f = tk.Frame(upper_f, width=150,height=100)
        buttons_f.pack(side=tk.RIGHT,fill=tk.X) 

        # Start server button
        start_server_button = ttk.Button(buttons_f, text="Start Server", command=self.start_server)
        start_server_button.pack(pady=4,ipadx=5, ipady=5, expand=True,fill=tk.BOTH)
        # Stop server button
        stop_server_button = ttk.Button(buttons_f, text="Stop server", command=self.stop_server)
        stop_server_button.pack(ipadx=5, ipady=5, expand=True,fill=tk.BOTH)

        # Separator
        separator = ttk.Separator(server_frame,orient="horizontal")
        separator.pack(fill=tk.X)

        # Server status labels
        server_status_f = tk.Frame(server_frame,width=200, height=100)
        server_status_f.pack(padx=5,pady=5,fill=tk.X)
        ss_cl = tk.Label(server_status_f,text="[SERVER STATUS]:")
        ss_cl.pack(fill=tk.X,side=tk.LEFT)
        server_status_label = tk.Label(server_status_f,textvariable=self.server_status_text)
        server_status_label.pack(fill=tk.X,side=tk.LEFT)
        #server_exceptions_label = tk.Label(server_status_f,textvariable=self.server_exceptions_text)
        #server_exceptions_label.pack(fill=tk.X)

    def set_directory(self):
        """Changes the path that the server uses to save the image"""
        if self.server_on:
            self.pop_up_window("Server ONLINE", "The server is ONLINE")
            return
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
            self.pop_up_window("Camera not selected", "Please select a camera.")
            return
        if self.server_on:
            self.pop_up_window("Server ON", "The server is waiting for requests to use the camera.")
            return

        utils.show_frames(self.channels,self.selected_cam.get())

    def start_server(self):
        if self.server_on:
            return
        if self.selected_cam.get() == "":
            self.pop_up_window("Camera not selected", "Please select a camera before turning on the server")
            return
        if self.image_path.get() == "":
            self.pop_up_window("Path not selected", "Please select the path for the image")
            return
        port = 0
        try:
            port = int(self.PORT.get())
        except ValueError:
            self.pop_up_window("Invalid Input", "The introduced PORT value is not a number.")
            return

        thread = threading.Thread(name="Server listening for connections",target=self.server.start,args=(self.selected_cam,self.channels,self.HOST,port))
        thread.start()
        self.server_on = True

    def stop_server(self):
        if not self.server_on:
            return
        self.server_on = False
        self.server.close()
    
    def pop_up_window(self,window_title,text):
        messagebox.showinfo(window_title,  text)

    def on_closing(self):
        if self.server_on:
            self.stop_server()
        self.destroy()