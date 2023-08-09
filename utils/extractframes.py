from datetime import timedelta
import cv2
import numpy as np
import os
import sys

usage_hint = """
    Description: Extracts frames or windows of consec frames from a video file using OpenCV and saves them as .jpg files in a folder with the same name as the video file.

    Usage: python ./extractframes.py [Options] <path_to_video> <frames_per_second> <window_size>

    Options:
        -h, --help: Show this help message and exit

    Arguments:
        path_to_video: Path to the video file to extract frames from
        frames_per_second: How many frames per second to save, if not given, defaults to 1 frame per second
        window_size: Size of the Window to sample, if not given, defaults to 1 frame

    Examples: 
    [1]: Extracts 1 frames per second from the video.
         $ python extractframes.py "C:/Users/username/Desktop/video.mp4"
    [2]: Extracts 15 frames per second from the video.
         $ python extractframes.py "C:/Users/username/Desktop/video.mp4" 15
    [3]: Extracts 2 windows of frames per second from the video, with a window size of 5 frames.
         $ python extractframes.py "C:/Users/username/Desktop/video.mp4" 2 5
"""


class FrameExtractor:
    """
        FrameExtractor that separates a video into separate frames using opencv library
    """

    def __init__(self, video_file, fps_to_save, window_size):
        # set fps to save, e.g. a video of 10 seconds with 10 fps saves 100 frames
        self.video_file = video_file
        self.frames_to_save_per_sec = fps_to_save
        self.window_size = window_size

    def main(self):
        filename, _ = os.path.splitext(self.video_file)
        filename += "-opencv"

        if not os.path.isdir(filename):  # make folder for video if nonexistent
            os.mkdir(filename)

        cap = cv2.VideoCapture(self.video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)  # get original fps of video

        # check if the desired fps given the window size requires more frames than the source video can provide
        saving_frames_per_second = min(fps//self.window_size, self.frames_to_save_per_sec)

        saving_frames_spots = get_saving_frames_spots(cap, saving_frames_per_second, self.window_size)

        count = 0
        while True:
            frame_duration = count / fps
            try:
                closest_spot = saving_frames_spots[0]
            except IndexError:
                break

            if frame_duration >= closest_spot:
                for i in range(self.window_size):
                    count += 1
                    is_read, frame = cap.read()
                    if not is_read:
                        # no more frames to read
                        break
                    formatted_frame_time = format_time(timedelta(seconds=frame_duration + i/fps))
                    cv2.imwrite(os.path.join(filename, f"frame{formatted_frame_time}.jpg"), frame)

                try:
                    saving_frames_spots.pop(0)
                except IndexError:
                    pass
            else:
                # discard all frames outside of the window
                is_read, frame = cap.read()
                if not is_read:
                    # no more frames to read
                    break
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


def get_saving_frames_spots(cap, saving_fps, size_window):
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
    try:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print(usage_hint)
            exit(0)
        # read arguments
        video_file = sys.argv[1]
        fps_to_save = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        win_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    except IndexError:
        print(usage_hint)
        exit(1)

    f = FrameExtractor(video_file, fps_to_save, win_size)
    f.main()