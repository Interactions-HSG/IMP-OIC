import time
import signal

import cv2
import numpy as np

class Camera():
    """
    Webcam access from: https://stackoverflow.com/questions/604749/how-do-i-access-my-webcam-in-python
    Movement detection from: http://www.robindavid.fr/opencv-tutorial/motion-detection-with-opencv.html
    """

    def __init__(self, device=0, preview=False, threshold=8):
        self.preview = preview
        self.vc = cv2.VideoCapture(device)
        _, self.frame = self.vc.read()
        self.height, self.width, _ = self.frame.shape
        self.nb_pixels = self.width * self.height

        self.min_threshold = (self.nb_pixels / 100) * threshold
        # Main results matrix
        self.res = np.zeros([self.height, self.width], dtype="uint8")
        # Make grayscale frame at t-1
        self.frame1gray = np.zeros([self.height, self.width], dtype="uint8")
        self.frame1gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        # Make empty frame at t
        self.frame2gray = np.zeros([self.height, self.width], dtype="uint8")
        # Last detection
        self.detection_time = 0
        self.movement_threshold = 20 # number of frames before movement alert is triggered
        self.movement_counter = 0
        signal.signal(signal.SIGINT, self.close)

    def run(self):
        if self.preview:
            cv2.namedWindow("Preview")

        if self.vc.isOpened():  # try to get the first frame
            rval, frame = self.vc.read()
        else:
            rval = False
            print("Failed to open camera")

        startT = time.time()

        # Wait for light adjustment of webcam
        while time.time() < startT + 2:
            time.sleep(0.05)

        while rval:
            if self.preview:
                cv2.imshow("Preview", frame)
            rval, frame = self.vc.read()
            instant = time.time()
            self.processImage(frame)

            if self.movement_detected():
                self.detection_time = instant
                print(f"Movement detected at {self.detection_time}")
            self.frame1gray = self.frame2gray


    def export_image(self, frame):
        pass

    def close(self, signum, frame):
        print("Closing camera")
        self.vc.release()
        cv2.destroyWindow("preview")

    def movement_detected(self):
        nb = self.nb_pixels - cv2.countNonZero(self.res)
        # Calculate the average of black pixel in the image
        if nb > self.min_threshold:
            if self.movement_counter > self.movement_threshold:
                self.movement_counter = 0
                return True
            else:
                self.movement_counter += 1
                return False
        else:
            self.movement_counter = 0
            return False

    def processImage(self, frame):
        # Converts image to grayscale
        self.frame2gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # Compare difference between frames and store into res
        self.res = cv2.absdiff(self.frame1gray, self.frame2gray)

        # Blur and morphologies
        self.res = cv2.blur(self.res, [5, 5])
        self.res = cv2.morphologyEx(self.res, cv2.MORPH_OPEN, None)
        self.res = cv2.morphologyEx(self.res, cv2.MORPH_CLOSE, None)
        # Cut at threshold
        _, self.res = cv2.threshold(self.res, 10, 255, cv2.THRESH_BINARY_INV)


if __name__ == "__main__":
    cam = Camera(0, preview=False)
    cam.run()