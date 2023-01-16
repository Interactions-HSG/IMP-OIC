from datetime import timedelta
import cv2
import numpy as np
import os
import sys


class FrameExtractor:
    """
        FrameExtractor that separates a video into separate frames using opencv library
    """

    def __init__(self, fps_to_save, video_file):
        # set fps to save, e.g. a video of 10 seconds with 10 fps saves 100 frames
        self.frames_to_save_per_sec = fps_to_save
        self.video_file = video_file

    def main(self):
        filename, _ = os.path.splitext(self.video_file)
        filename += "-opencv"

        if not os.path.isdir(filename):  # make folder for video if nonexistent
            os.mkdir(filename)

        cap = cv2.VideoCapture(self.video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)  # get original fps of video

        saving_frames_per_second = min(fps, self.frames_to_save_per_sec)  # if video fps > our fps, set it to that
        saving_frames_spots = get_saving_frames_spots(cap, saving_frames_per_second)

        count = 0
        while True:
            is_read, frame = cap.read()
            if not is_read:
                # no frames to read
                break

            frame_duration = count / fps
            try:
                closest_spot = saving_frames_spots[0]
            except IndexError:
                break

            if frame_duration >= closest_spot:
                formatted_frame_time = format_time(timedelta(seconds=frame_duration))
                cv2.imwrite(os.path.join(filename, f"frame{formatted_frame_time}.jpg"), frame)

                try:
                    saving_frames_spots.pop(0)
                except IndexError:
                    pass

            count += 1


def format_time(td):
    """
        Format timedelta object by returning a nice string representation omitting microseconds
        and retaining milliseconds (e.g 00:00:10.05)
    """
    result = str(td)
    try:
        result, ms = result.split(".")
    except ValueError:
        return (result + ".00").replace(":", "-")
    ms = int(ms)
    ms = round(ms / 1e4)
    return f"{result}.{ms:02}".replace(":", "-")


def get_saving_frames_spots(cap, saving_fps):
    """
        Takes the VideoCapture object from OpenCV and returns a list of duration spots on which to save the frames
    """
    s = []
    # get duration with nr of frames divided by the number of fps
    clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    for i in np.arange(0, clip_duration, 1 / saving_fps):
        s.append(i)
    return s


if __name__ == "__main__":
    """
    First arg: path to video
    Second arg: How many frames per second
    """
    video_file = sys.argv[1]
    fps_to_save = int(sys.argv[2])
    f = FrameExtractor(fps_to_save, video_file)
    f.main()
