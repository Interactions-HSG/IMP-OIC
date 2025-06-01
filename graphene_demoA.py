import os
import subprocess
import argparse
import tqdm

from structures.graph import *
from utilities import inout
from cam import Camera
import shutil
import time

TEMP_DIR = "temp"
CAM_PATH = "cam"
OUT_DIR = "out"


class Graphene:
    """
        Creates scene graphs on frames / images and can call temporal graph creation
    """

    def __init__(self, alpha, min_assignment_conf):
        self.temp_dir = TEMP_DIR
        self.tg = TemporalGraph()
        self.alpha = alpha
        self.min_assignment_conf = min_assignment_conf

    def run_online(self, graph2text):
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
            self.tg.insert_framegraph(fg, self.alpha, self.min_assignment_conf)
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
                                 self.temp_dir + "/" + "%03d" % image_count + ".json")
            image_count += 1

    def classify_images_window(self, image_path, fps_to_save, window_size):
        """
        For all frames (images) in input folder, call scene graph generator
        """

        if os.path.isdir(self.temp_dir):
            os.rmdir(self.temp_dir)
        os.mkdir(self.temp_dir)

        if os.path.isdir(image_path + "/img"):
            os.rmdir(image_path + "/img")
        os.mkdir(image_path + "/img")

        if os.path.isdir(image_path + "/img/JSON"):
            os.rmdir(image_path + "/img/JSON")
        os.mkdir(image_path + "/img/JSON")

        images = sorted(os.listdir(image_path))
        images = inout.clean_img_list(images)

        #print("generating scene graphs:")
        for image_count, image in enumerate(tqdm.tqdm(images)):
            generate_scene_graph("RelTR", image_path + "/" + image,
                                 self.temp_dir + "/" + "%03d" % image_count + ".json")

        tmp_graphs = sorted(os.listdir(self.temp_dir))
        tmp_graphs = inout.clean_json_list(tmp_graphs)

        number_of_frames_to_select = window_size

        # combine tmp graphs into one graph per window. this will include duplictes of objects and needs to be cleaned in tg construction
        for graph_count, i in enumerate(range(0, len(tmp_graphs) // number_of_frames_to_select)):
            graph = []

            for j in range(i, (i + 1)):
                with open(self.temp_dir + "/" + tmp_graphs[j], "r") as file:
                    triples = json.load(file)
                    file.close()
                graph += triples
            with open(image_path + "/img/JSON/" + "%03d" % graph_count + ".json", "w") as file:
                json.dump(graph, file)
                file.close()

        print("copying images and cleaning up temporary files:")
        for image_count, image in enumerate(tqdm.tqdm(images)):
            # copy the middle image to img folder
            if image_count % number_of_frames_to_select == (number_of_frames_to_select // 2): #this limits the window size to at least 2
                # depending on your setup and OS replace the "copy /z" with "copy" for local windows directory and "cp" for linux and macOS  
                print(image_path + "/" + image, image_path + "/img/" + image)
                shutil.copy(image_path + "/" + image, image_path + "/img/" + image)

        # clean up temporary files and folders, move all graph files to a JSON folder in the image_path
        if os.path.isdir(image_path + "/JSON"):
            os.rmdir(image_path + "/JSON")
        os.replace(self.temp_dir, image_path + "/JSON")

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
            start = time.time()
            self.tg.insert_framegraph(fg, self.alpha, self.min_assignment_conf, verbose=True)
            end = time.time()
            duration = end - start
            print(duration)
            sg_count += 1

    def generate_temporal_graph_frames(self, scenegraphs_path, image_path):
        """
        Identical to generate_temporal_graph, but exports images with graph overlays
        """
        framegraph_pre = None
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
            start = time.time()
            self.tg.insert_framegraph(fg, self.alpha, self.min_assignment_conf, framegraph_pre, verbose=True)
            end = time.time()
            n_t = str(end - start)
            print("Temporalgraph population:" + n_t)
            self.tg.to_frame_plot(os.path.join(image_path, img), os.path.join(ann_path, str(sg_count)), fg)
            sg_count += 1
            framegraph_pre = fg

    def generate_temporal_graph_frames_no_plot(self, scenegraphs_path, image_path):
        """
        Identical to generate_temporal_graph_frames, but don't export images with graph overlays
        """
        framegraph_pre = None
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
            self.tg.insert_framegraph(fg, self.alpha, self.min_assignment_conf, framegraph_pre, verbose=True)
            #self.tg.to_frame_plot(os.path.join(image_path, img), os.path.join(ann_path, str(sg_count)), fg)
            sg_count += 1
            framegraph_pre = fg


def generate_scene_graph(reltr_path, img_path, graph_path, device="cpu", topk=10):
    """
    calls RelTR to create scene graph from image and saves json output file in graph path
    """
    try:

        subprocess.check_output([f'python',
                                 f"{reltr_path}/mkgraph.py",
                                 "--img_path", f"{img_path}",
                                 "--device", f"{device}",
                                 "--resume", f"{reltr_path}/ckpt/checkpoint0149.pth",
                                 "--export_path", f"{graph_path}",
                                 "--topk", f"{topk}"])
    except subprocess.SubprocessError as ex:
        print(ex)


def main(args):
    graphene = Graphene(args.alpha, args.min_confidence)

    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    if args.cam:
        graphene.run_online(args.text)
        return
    if args.img_path_window:
        graphene.classify_images_window(args.img_path_window, args.window_size)
        graph_path = args.img_path_window + "/img/JSON"
        graphene.generate_temporal_graph_frames(graph_path, args.img_path_window + "/img")
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
    parser.add_argument("--img_path_window", type=str,
                        help="Directory of existing images sets (.jpeg, .jpg, .png) for bulk processing")
    parser.add_argument("--window_size", type=int, default=5,
                        help="amount of frames in the window")
    parser.add_argument("--img_path", type=str,
                        help="Directory of existing images (.jpeg, .jpg, .png) for bulk processing")
    parser.add_argument("--graph_path", type=str,
                        help="Directory of existing scenegraphs (.json) for bulk processing")
    parser.add_argument("--cam", type=bool, default=False,
                        help="Run graphene on webcam")
    parser.add_argument("--text", type=str,
                        help="Export graph as natural language text for language model inference under this path")
    parser.add_argument("--min_confidence", type=float, default=0.6,
                        help="The minimum confidence required to match an object from one frame to the next")
    parser.add_argument("--alpha", type=float, default=0.3,
                        help="Sets similarity metrics as alpha * neighbour similarity + (1-alpha) * spatial similarity")
    parser.add_argument("--visual", type=str,
                        help="Plots the temporal graph in 3d space")
    main(parser.parse_args())
