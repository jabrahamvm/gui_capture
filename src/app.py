import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import cv2
import wmi

def find_cameras():
    def list_ports():
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        is_working = True
        dev_port = 0
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
                print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camera.read()
                if is_reading:
                    print("Port %s is working" %(dev_port))
                    available_ports.append(dev_port)
                else:
                    print("Port %s is present but does not reads." %(dev_port))
                    available_ports.append(dev_port)
            dev_port +=1
        return available_ports


    def list_usb_devices():
        """
        Return a list of external USB cameras
        Implementation of this function has Windows-only compatibility.
        """
        c = wmi.WMI()
        cameras = []
        wql = "Select * From Win32_USBControllerDevice"
        for item in c.query(wql):
            pnp = item.Dependent.PNPClass
            service = item.Dependent.Service
            if pnp:
                if pnp.upper() == 'CAMERA' and service.upper() == 'USBVIDEO':
                    cameras.append(item.Dependent.Name)
        return cameras

    ports = list_ports()
    devices = list_usb_devices()
    channels = {}

    for i in range(len(ports)):
        channels[f"{devices[i]}"] = ports[i]

    return channels

channels = find_cameras()
root = tk.Tk()

# config the root window
root.geometry("400x400")
root.resizable(False, False)
root.title('Webcam test')

# create a combobox
selected_cam = tk.StringVar()
cb_label = ttk.Label(text="Please select a webcam:")
cb_label.pack(fill=tk.X, padx=5, pady=5)
cam_cb = ttk.Combobox(root, textvariable=selected_cam)
cam_cb.place(x=24, y=50)
cam_cb.configure(width=55)
cb_label.place(x=24, y=27)


# get values for the combobox
cam_cb['values'] = list(channels.keys())

# prevent typing a value
cam_cb['state'] = 'readonly'

# bind the selected value changes
def show_preview():
    """ handle the cam changed event """
    if selected_cam.get() == "":
        return
    cap = cv2.VideoCapture(channels[selected_cam.get()])
    show_frames(cap)

def callback():
    directory = filedialog.askdirectory()
    print(directory)

browse_btn = ttk.Button(text='Browse folder', command=callback)
browse_btn.pack(ipadx=5, ipady=5, expand=True)
browse_btn.place(x=111, y=88)

preview_btn = ttk.Button(root, text="Preview", command=show_preview)
preview_btn.pack(ipadx=5, ipady=5, expand=True)
preview_btn.place(x=220, y=88)

# Define function to show frame
def show_frames(cap):

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

root.mainloop()