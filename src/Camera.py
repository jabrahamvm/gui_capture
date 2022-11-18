import cv2
from imutils.video import WebcamVideoStream

class Camera(WebcamVideoStream):
    def __init__(self, src=0, name="WebcamVideoStream", resolution=(1920,1080)):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
    
    def stop(self):
        self.stopped = True
        if self.grabbed:
            self.stream.release()