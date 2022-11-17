
class FrameGenerator:
    
    def __init__(self, sample=1):
        self.frame_i = 0
        if sample == 1:
            # TODO: Load sample 1
        elif sample == 2:
            # TODO: Load sample 2
        else:
            print(f"{sample} is no valid sample")
            self.frames = []

    def get_next_frame():
        frame = self.frames[]
        self.frame_i += 1
        return frame
    
    def has_next():
        return self.frame_i <= len(self.frames) - 1

