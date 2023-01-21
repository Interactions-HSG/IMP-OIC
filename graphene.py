import os
import subprocess
import argparse
import tqdm

from structures.graph import *
from utils import inout
from cam import Camera

TEMP_DIR = "temp"
CAM_PATH = "cam"
OUT_DIR = "out"
min_assignment_conf = 0.6

class Graphene:
    """
        Creates scene graphs on frames / images and can call temporal graph creation
    """

    def __init__(self):
        self.temp_dir = TEMP_DIR
        self.tg = TemporalGraph()

    def run_online(self, min_confidence, alpha, graph2text):
        if os.path.isdir(self.temp_dir):
            os.rmdir(self.temp_dir)
        os.mkdir(self.temp_dir)

        img_name = "img.png"
        scenegraph_name = "scenegraph.json"

        cam = Camera(export_path=CAM_PATH)
        frame_count = 0
        while True:
            cam.get_image(img_name)
            generate_scene_graph("RelTR", os.path.join(CAM_PATH, img_name),
                                 os.path.join(self.temp_dir, scenegraph_name))
            frame_count += 1
            fg = FrameGraph()
            fg.create_graph(os.path.join(self.temp_dir, scenegraph_name))
            self.tg.insert_framegraph(fg, min_confidence, alpha)
            if graph2text:
                self.tg.to_text(os.path.join(OUT_DIR, graph2text))


    def classify_images(self, image_path):
        """
        For all frames (images) in input folder, call scene graph generator
        """
        if os.path.isdir(self.temp_dir):
            os.rmdir(self.temp_dir)
        os.mkdir(self.temp_dir)

        images = sorted(os.listdir(image_path))
        images = inout.clean_img_list(images)
        image_count = 0
        for image in tqdm.tqdm(images):
            generate_scene_graph("RelTR", image_path + "/" + image,
                                 self.temp_dir + "/" + str(image_count) + ".json")
            image_count += 1

    def generate_temporal_graph(self, scenegraphs_path):
        """
        For all scene graphs of individual frames, create frame graph and update temporal graph
        """
        scene_graphs = sorted(os.listdir(scenegraphs_path))
        scene_graphs = inout.clean_json_list(scene_graphs)
        sg_count = 0
        for sg in scene_graphs:
            fg = FrameGraph(sg_count)
            fg.create_graph(scenegraphs_path + "/" + sg)
            self.tg.insert_framegraph(fg, min_assignment_conf, verbose=True)
            sg_count += 1
            
    def generate_temporal_graph_frames(self, scenegraphs_path, image_path):
        """
        Identical to generate_temporal_graph, but exports images with graph overlays
        """
        scene_graphs = sorted(os.listdir(scenegraphs_path))
        scene_graphs = inout.clean_json_list(scene_graphs)
        images = sorted(os.listdir(image_path))
        images = inout.clean_img_list(images)
        ann_path = os.path.join(image_path, "annotated")
        if not os.path.isdir(ann_path):
            os.mkdir(ann_path)
        sg_count = 0
        for sg, img in zip(scene_graphs, images):
            fg = FrameGraph(sg_count)
            fg.create_graph(os.path.join(scenegraphs_path, sg))
            self.tg.insert_framegraph(fg, min_assignment_conf, verbose=True)
            self.tg.to_frame_plot(os.path.join(image_path, img), os.path.join(ann_path, str(sg_count)), sg_count)
            sg_count += 1


def generate_scene_graph(reltr_path, img_path, graph_path, device="cpu", topk=7):
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

    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    if args.cam:
        graphene.run_online(args.min_confidence, args.alpha, args.text)
        return
    if args.img_path:
        graphene.classify_images(args.img_path)
        graph_path = TEMP_DIR
        graphene.generate_temporal_graph_frames(graph_path, args.img_path)
    if args.graph_path:
        graph_path = args.graph_path
        graphene.generate_temporal_graph(graph_path)

    if args.visual:
        graphene.tg.to_plot(os.path.join(OUT_DIR, args.visual))

    if args.text:
        graphene.tg.to_text(os.path.join(OUT_DIR, args.text))


if __name__ == "__main__":
    os.environ['MKL_THREADING_LAYER'] = 'GNU'  # Required on some machines for running tensorflow-cpu
    parser = argparse.ArgumentParser("graphene")
    parser.add_argument("--img_path", type=str,
                        help="Directory of existing images (.jpeg, .jpg, .png) for bulk processing")
    parser.add_argument("--graph_path", type=str,
                        help="Directory of existing scenegraphs (.json) for bulk processing")
    parser.add_argument("--cam", type=bool, default=False,
                        help="Run graphene on webcam")
    parser.add_argument("--text", type=str,
                        help="Export graph as natural language text for language model inference under this path")
    parser.add_argument("--min_confidence", type=float, default=0.1,
                        help="The minimum confidence required to match an object from one frame to the next")
    parser.add_argument("--alpha", type=float, default=0.3,
                        help="Sets similarity metrics as alpha * neighbour similarity + (1-alpha) * spatial similarity")
    parser.add_argument("--visual", type=str,
                        help="Plots the temporal graph in 3d space")
    main(parser.parse_args())
