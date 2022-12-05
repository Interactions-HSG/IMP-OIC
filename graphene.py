import os
import subprocess
import matplotlib.pyplot as plt

from structures.graph import *


class Graphene:
    """
        Creates scene graphs on frames / images and can call temporal graph creation
    """

    def __init__(self, path):
        self.triples = set()
        self.input_folder_path = path
        self.output_folder_path = "frames"

    def run(self):
        """
            For all frames (images) in input folder, call scene graph generator
        """
        images = os.listdir(self.input_folder_path)
        image_count = 0
        for image in images:
            # check if valid image file
            if image[-4:] == ".jpg":
                generate_scene_graph("RelTR", self.input_folder_path + "/" + image,
                                     self.output_folder_path + "/" + str(image_count) + ".json")
                image_count += 1

    def generate_temporal_graph(self):
        """
            For all scene graphs of individual frames, create frame graph and update temporal graph
        """
        scene_graphs = os.listdir(self.output_folder_path)
        sg_count = 0
        tg = TemporalGraph()
        for sg in scene_graphs:
            fg = FrameGraph(sg_count)
            fg.create_graph(self.output_folder_path + "/" + sg)
            sg_count += 1
            tg.insert_framegraph(fg, 0.1, verbose=True)

    def visualise(self, img_path):
        fig, ax = plt.subplots()
        im = plt.imread(img_path)
        ax.imshow(im)
        for triple in self.triples:
            (oxmin, oymin, oxmax, oymax) = triple.obox
            (sxmin, symin, sxmax, symax) = triple.sbox
            oxcentre = oxmin + (oxmax - oxmin) / 2
            oycentre = oymin + (oymax - oymin) / 2
            sxcentre = sxmin + (sxmax - sxmin) / 2
            sycentre = symin + (symax - symin) / 2
            xlinecentre = oxcentre + (sxcentre - oxcentre) / 2
            ylinecentre = oycentre + (sycentre - oycentre) / 2
            ax.add_patch(plt.Rectangle((sxmin, symin), sxmax - sxmin, symax - symin,
                                       fill=False, color='blue', linewidth=2.5))
            ax.add_patch(plt.Rectangle((oxmin, oymin), oxmax - oxmin, oymax - oymin,
                                       fill=False, color='orange', linewidth=2.5))
            ax.annotate(triple.subject, (sxmin, symin), color="white")
            ax.annotate(triple.object, (oxmin, oymin), color="white")
            # ax.add_patch(plt.Arrow((sxcentre, sycentre), (oxcentre, oycentre), color="red"))
            ax.annotate(triple.predicate, (xlinecentre, ylinecentre), color="white")
        plt.show(block=False)
        plt.show()


def generate_scene_graph(reltr_path, img_path, graph_path, device="cpu", topk=5):
    """
        calls RelTR to create scene graph from image and saves json output file in graph path
    """
    subprocess.check_output([f'python',
                             f"{reltr_path}/mkgraph.py",
                             "--img_path", f"{img_path}",
                             "--device", f"{device}",
                             "--resume", f"{reltr_path}/ckpt/checkpoint0149.pth",
                             "--export_path", f"{graph_path}",
                             "--topk", f"{topk}"])


if __name__ == "__main__":
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    path_to_images = "test_videos/test0-opencv"
    graphene = Graphene(path_to_images)
    # uncomment following line if new test video should be initially parsed
    # graphene.run()
    graphene.generate_temporal_graph()
