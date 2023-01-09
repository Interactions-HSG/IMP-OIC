import networkx as nx
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from PIL import Image
import uuid
import numpy as np

import utils.plot
from structures.scene import SceneObject
from structures.definitions import name_similarity, convert_to_text
from utils import plot


class FrameGraph:

    def __init__(self, frame_id):
        self.g = nx.DiGraph()
        self.frame_id = frame_id

    def create_graph(self, graph_path):
        """
            Creates graph for a single frame
        """
        similarity_tol = 0.3

        print("Creating frame graph...")
        with open(graph_path, "r") as file:
            triples = json.load(file)
            file.close()

        for triple_dict in triples:
            sub = triple_dict["subject"]
            pred = triple_dict["predicate"]
            obj = triple_dict["object"]
            # print("Got triple: subj = ", sub, " pred = ", pred, " obj = ", obj)
            sub_obj = SceneObject(sub["id"], sub["xmin"], sub["ymin"], sub["xmax"], sub["ymax"])

            predicate = pred["id"]
            obj_obj = SceneObject(obj["id"], obj["xmin"], obj["ymin"], obj["xmax"], obj["ymax"])

            graph_subj = self.get_closest_node(sub_obj, epsilon=similarity_tol)
            graph_obj = self.get_closest_node(obj_obj, epsilon=similarity_tol)

            # adding nodes and edges gets ignored in graph if already exists so no additional check necessary
            self.g.add_node(graph_subj)
            self.g.add_node(graph_obj)
            self.g.add_edge(graph_subj, graph_obj, relation=predicate)

    def get_closest_node(self, subj, epsilon=0.3):
        """
            Check if node already exists in graph or is sufficiently similar for same frame to identify same objects
            return that node if exists, otherwise the original node
        """
        for node in self.g.nodes:
            if subj.approximately_same(node, epsilon):
                return node
        return subj

    def test_frame_graph(self):
        # path_to_result = "eval/reltr/2398798.json"
        path_to_result1 = "../eval/reltr/glass/0.json"
        self.create_graph(path_to_result1)
        plot.draw_graph(self.g, "eval/test/result1.png")
        print("Result 1 created! ")

        path_to_result2 = "../eval/reltr/glass/1.json"
        self.create_graph(path_to_result2)
        plot.draw_graph(self.g, "eval/test/result2.png")
        print("Result 2 created! ")

        path_to_result3 = "../eval/reltr/glass/2.json"
        self.create_graph(path_to_result3)
        plot.draw_graph(self.g, "eval/test/result3.png")
        print("Result 3 created! ")

        # open image of graph
        im1 = Image.open("../eval/test/result1.png")
        im2 = Image.open("../eval/test/result2.png")
        im3 = Image.open("../eval/test/result3.png")
        im1.show()
        im2.show()
        im3.show()


class TemporalGraph:

    def __init__(self):
        self.g = nx.Graph()
        self.frame_ids = []

    def insert_framegraph(self, framegraph, min_assignment_conf=0.1, alpha=0.3, verbose=False):
        '''
        Inserts a framegraph into the temporal graph by matching nodes when their similarity is above min_assignment_conf.
        Similarity is determined by alpha * neighbour similarity + (1-alpha) * spatial similarity
        '''
        if verbose:
            print(f"-------------\nInserting framegraph with id {framegraph.frame_id}\n-------------")
        self.frame_ids.append(framegraph.frame_id)
        temporal_nodes = set(self.g.nodes)
        f2t = {}  # Maps from FrameNode to node identifier in temporal graph

        for f in framegraph.g.nodes():
            best_match = None
            best_similarity = -1
            for t in temporal_nodes:

                # Count how many neighbours are shared
                neigh_similarity = 0
                neighbor_matches = 0
                n_neighbours = len(self.g[t])
                if n_neighbours > 0:
                    for nt in self.g[t]:
                        for nf in framegraph.g[f]:
                            if self.g.nodes[nt]["content"].name == nf.name:
                                neighbor_matches += 1
                    neigh_similarity = neighbor_matches / len(self.g[t])

                # Compare bounding box similarity
                spat_similarity = f.box_similarity(self.g.nodes[t]["content"])

                # Compare name similarity
                n_similarity = name_similarity(f.name, self.g.nodes[t]["content"].name)

                similarity = (alpha * neigh_similarity + (1-alpha) * spat_similarity + n_similarity) / 2

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = t

            # Add or update node
            if best_similarity < min_assignment_conf:
                uid = str(uuid.uuid4())[0:4]
                node_identifier = f"{f.name}_{uid}"
                self.g.add_node(node_identifier, content=f)
                f2t[f] = node_identifier
                self.g.nodes[node_identifier]["frames"] = set()
                print(f"Creating new node {node_identifier} for {f.name} and match confidence {best_similarity}")
            else:
                self.g.nodes[best_match]["content"] = f
                temporal_nodes.remove(best_match)  # Reduce matching space
                f2t[f] = best_match
                print(f"Updating node {best_match} with {f.name} and match confidence {best_similarity}")
            self.g.nodes[f2t[f]]["frames"].add(framegraph.frame_id)

        for n1, n2 in framegraph.g.edges:
            if framegraph.g[n1][n2]["relation"]:
                relation = framegraph.g[n1][n2]["relation"]
            else:
                relation = "Unknown"

            if (f2t[n1], f2t[n2]) not in self.g.edges:  # If edge does not exist
                d = {framegraph.frame_id: relation}
                self.g.add_edge(f2t[n1], f2t[n2], relations=d)
                print(f"Creating new edge: {n1} {relation} {n2}")
            else:  # append to edge
                self.g[f2t[n1]][f2t[n2]]["relations"][framegraph.frame_id] = relation
                print(f"Updating edge: {n1} {relation} {n2}")


    def to_text(self, export_path):
        # For each entity, report what happened to it
        stories = []
        for n1, n2 in self.g.edges:
            relations = self.g[n1][n2]["relations"]
            for (frame, relation) in relations.items():
                relation_text = convert_to_text(relation)
                story = f"{n1} {relation_text} {n2} in frame {frame}. "
                stories.append(story)
        with open(export_path, "w") as file:
            file.write("".join(stories))
            file.close()

    def to_plot(self, export_path):
        """
        Plots the temporal graph in 3d space.
        Inspired by https://stackoverflow.com/questions/60392940/multi-layer-graph-in-networkx
        """
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_axis_off()
        cmap = plt.get_cmap("plasma")
        colors = cmap(np.linspace(0, 1, len(self.g.nodes)))
        node2color = dict(zip(self.g.nodes, colors))

        positions = nx.spring_layout(self.g)
        xmin, ymin = np.min(list(positions.values()), axis=0)
        xmax, ymax = np.max(list(positions.values()), axis=0)

        for i, f in enumerate(self.frame_ids):
            # Plot the surface of frame f
            x = np.linspace(xmin, xmax, 10)
            y = np.linspace(ymin, ymax, 10)
            z = np.ones([len(x), len(y)]) * i
            x, y = np.meshgrid(x, y)
            ax.plot_surface(x, y, z, alpha=0.2, zorder=1)
            ax.text(xmin, ymin, i, f"Frame {f}", fontsize="small")

            # Plot edges
            graph_segments = []
            for n1, n2 in self.g.edges:
                if f in self.g[n1][n2]["relations"].keys():  # Check whether edge (n1, n2) exists in frame f
                    graph_segments.append(((*positions[n1], i), (*positions[n2], i)))
            ax.add_collection3d(Line3DCollection(graph_segments, color="k", alpha=0.5, linestyle="-", linewidth=0.5, zorder=2))

            # Plot nodes
            time_segments = []
            for n in self.g.nodes:
                if f in self.g.nodes[n]["frames"]:  # Check whether node n exists in frame f
                    ax.scatter(*positions[n], i, color=node2color[n], s=50, zorder=3)
                    ax.text(*positions[n], i, n, fontsize='xx-small', horizontalalignment='center', verticalalignment='center', zorder=100)
                    # Draw edges between frames
                    if i != 0:
                        prev_f = self.frame_ids[i-1]
                        if prev_f in self.g.nodes[n]["frames"]: # if node existed in previous frame
                            time_segments.append(((*positions[n], i-1), (*positions[n], i)))
            ax.add_collection3d(Line3DCollection(time_segments, color="k", alpha=0.3, linestyle="--", linewidth=0.5, zorder=2))
        plt.savefig(export_path, dpi=300, bbox_inches="tight")


def test_temporal_graph():
    fg1 = FrameGraph(1)
    fg1.create_graph("../eval/reltr/glass/0.json")

    fg2 = FrameGraph(2)
    fg2.create_graph("../eval/reltr/glass/1.json")

    fg3 = FrameGraph(3)
    fg3.create_graph("../eval/reltr/glass/2.json")

    tg = TemporalGraph()
    tg.insert_framegraph(fg1, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg2, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg3, 0.1, 0.5, verbose=True)
    utils.plot.draw_reltr_image("../eval/img/glass/1.png", "../eval/reltr/glass/1.json")

def test_temporal_graph_to_text():
    fg1 = FrameGraph(1)
    fg1.create_graph("../eval/reltr/glass/0.json")

    fg2 = FrameGraph(2)
    fg2.create_graph("../eval/reltr/glass/1.json")

    fg3 = FrameGraph(3)
    fg3.create_graph("../eval/reltr/glass/2.json")

    tg = TemporalGraph()
    tg.insert_framegraph(fg1, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg2, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg3, 0.1, 0.5, verbose=True)

    print(tg.to_text())

def test_temporal_graph_to_plot():
    fg1 = FrameGraph(1)
    fg1.create_graph("../eval/reltr/glass/0.json")

    fg2 = FrameGraph(2)
    fg2.create_graph("../eval/reltr/glass/1.json")

    fg3 = FrameGraph(3)
    fg3.create_graph("../eval/reltr/glass/2.json")

    tg = TemporalGraph()
    tg.insert_framegraph(fg1, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg2, 0.1, 0.5, verbose=True)
    tg.insert_framegraph(fg3, 0.1, 0.5, verbose=True)

    print(tg.to_plot("temporal.png"))

if __name__ == "__main__":
    # g = FrameGraph(0)
    # g.test_frame_graph()
    # test_temporal_graph()
    # test_temporal_graph_to_text()
    test_temporal_graph_to_plot()

