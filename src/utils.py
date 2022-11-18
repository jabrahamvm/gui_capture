import cv2
import wmi
import imutils
from Camera import Camera

WIDTH = 10000
HEIGHT = 10000

def find_cameras():
    def list_ports():
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        is_working = True
        dev_port = 0
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
            if not camera.isOpened():
                is_working = False
                #print("Port %s is not working." %dev_port)
            else:
                is_reading, _ = camera.read()
                if is_reading:
                    #print("Port %s is working" %(dev_port))
                    available_ports.append(dev_port)
                else:
                    #print("Port %s is present but does not reads." %(dev_port))
                    available_ports.append(dev_port)
            dev_port += 1
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

# Define function to show frame
def show_frames(channels, camera):
    stream = cv2.VideoCapture(channels[camera], cv2.CAP_DSHOW)
    #stream.start()
    while True:
        grabbed, frame = stream.read()
        # if frame is read correctly ret is True
        if not grabbed:
            break

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, 'PRESS "Q" TO EXIT', (50, 50), font, 1, (0, 255, 255), 2, cv2.LINE_4)

        # Display the resulting frame
        cv2.imshow("Camera's Preview", frame)
        if cv2.waitKey(1) == ord('q') or cv2.waitKey(1) == ord('Q'):
            break
    stream.release()
    cv2.destroyAllWindows()

def capture_image(cap, path=""):
    frame = cap.read()
    cv2.imwrite(path + "image.jpg", frame)