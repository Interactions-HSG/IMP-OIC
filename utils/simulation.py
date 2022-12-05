class FrameGenerator:
    
    def __init__(self):
        self.frame_i = 0
        self.frames = [
            "eval/reltr/0.json",
            "eval/reltr/1.json",
            "eval/reltr/2.json",
        ]

    def next(self):
        frame = self.frames[self.frame_i]
        self.frame_i += 1
        return frame
    
    def has_next(self):
        return self.frame_i < len(self.frames)

