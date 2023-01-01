import signal
import time

import cv2


class Camera:

    def __init__(self, device=0, export_path="."):
        self.vc = cv2.VideoCapture(device)

        signal.signal(signal.SIGINT, self.close)
        self.export_path = export_path

    def get_image(self, filename):
        if self.vc.isOpened():  # try to get the first frame
            rval, frame = self.vc.read()
            self.export_image(frame, filename)
        else:
            rval = False
            print("Failed to open camera")

    def export_image(self, frame, filename):
        fname = f"{self.export_path}/{filename}"
        cv2.imwrite(fname, frame)

    def close(self, signum, frame):
        print("Closing camera")
        self.vc.release()


if __name__ == "__main__":
    cam = Camera(0)
    time.sleep(1)
    cam.get_image("cam.png")
