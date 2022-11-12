import os
import subprocess
import time

import matplotlib.pyplot as plt

import parser
from cam import Camera

import json

class Graphene():

    def __init__(self):
        self.triples = set()
        self.addQueue = set()
        self.graph_path = "graph.json"
        self.img_path = "snap.jpg"
        self.camera = None


    def run(self):
        self.camera = Camera(device=0, preview=False, threshold=5, export_path=self.img_path)
        while(True):
            self.update()

    def update(self):
        # Get image (once the camera returns, we know there was movement, everything is synchronous)
        # self.camera.run()
        print("--------------------")
        print("Change detected. Generating graph...")

        # Call scene graph generator and import triples
        # self.generate_scene_graph("RelTR", self.img_path, self.graph_path)
        read_triples = parser.parse_triples(self.graph_path)

        # # TODO: make better output
        # for drop in dropped_triples:
        #     print(f"{drop.object} {drop.predicate} {drop.subject} has dropped out." )
        #
        # for new in new_triples:
        #     print(f"{new.subject} {new.predicate} {new.object} has popped up.")
        #     # self.addQueue.add(new)

        self.triples = read_triples # currently, we show everything detected
        self.visualise(self.img_path)
        time.sleep(2) # when we do not use webcam

    def generate_scene_graph(self, reltr_path, img_path, graph_path, device="cpu"):
        subprocess.check_output([f'python',
                                 f"{reltr_path}/mkgraph.py",
                                 "--img_path", f"{img_path}",
                                 "--device", f"{device}",
                                 "--resume", f"{reltr_path}/ckpt/checkpoint0149.pth",
                                 "--export_path", f"{graph_path}"])


    def visualise(self, img_path):
        fig, ax = plt.subplots()
        im = plt.imread(img_path)
        ax.imshow(im)
        for triple in self.triples:
            (oxmin, oymin, oxmax, oymax) = triple.obox
            (sxmin, symin, sxmax, symax) = triple.sbox
            ax.add_patch(plt.Rectangle((sxmin, symin), sxmax - sxmin, symax - symin,
                                       fill=False, color='blue', linewidth=2.5))
            ax.add_patch(plt.Rectangle((oxmin, oymin), oxmax - oxmin, oymax - oymin,
                                       fill=False, color='orange', linewidth=2.5))
            ax.set_title(triple.subject + ' ' + triple.predicate + ' ' + triple.object, fontsize=10)
        plt.show()




if __name__ == "__main__":
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    graphene = Graphene()
    graphene.run()
