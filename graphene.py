import os
import subprocess
import argparse

from structures.graph import *

TEMP_DIR = "temp"

class Graphene:
    """
        Creates scene graphs on frames / images and can call temporal graph creation
    """

    def __init__(self):
        self.temp_dir = TEMP_DIR
        self.tg = TemporalGraph()

    def classify_images(self, image_path):
        """
        For all frames (images) in input folder, call scene graph generator
        """
        if os.path.isdir(self.temp_dir):
            os.rmdir(self.temp_dir)
        os.mkdir(self.temp_dir)

        images = os.listdir(image_path)
        image_count = 0
        for image in images:
            # check if valid image file
            if image[-4:] == ".jpg" or image[-5:] == ".jpeg":
                generate_scene_graph("RelTR", image_path + "/" + image,
                                     self.temp_dir + "/" + str(image_count) + ".json")
                image_count += 1

    def generate_temporal_graph(self, scenegraphs_path):
        """
        For all scene graphs of individual frames, create frame graph and update temporal graph
        """
        scene_graphs = os.listdir(scenegraphs_path)
        sg_count = 0
        for sg in scene_graphs:
            fg = FrameGraph(sg_count)
            fg.create_graph(scenegraphs_path + "/" + sg)
            self.tg.insert_framegraph(fg, 0.1, verbose=True)
            sg_count += 1

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

def main(args):
    graphene = Graphene()
    if not os.path.isdir(args.out):
        os.mkdir(args.out)
    if args.cam:
        print("Camera feed is not supported yet")
        return
    if args.img_path:
        graphene.classify_images(args.img_path)
    if args.graph_path:
        graph_path = args.graph_path
    else:
        graph_path = TEMP_DIR
    graphene.generate_temporal_graph(graph_path)
    # TODO: export graph visualisation

    if args.text:
        text = graphene.tg.to_text()
        with open(os.join(args.out, "graph_text.txt"), "w") as file:
            file.write(text)
            file.close()



if __name__ == "__main__":
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    parser = argparse.ArgumentParser("Graphene")
    parser.add_argument("--img_path", type=str)
    parser.add_argument("--graph_path", type=str)
    parser.add_argument("--cam", type=bool, default=False)
    parser.add_argument("--out", type=str, default="out")
    parser.add_argument("--text", type=bool, default=True)
    main(parser.parse_args())
