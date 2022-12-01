import networkx as nx
import json
from structures.scene import SceneObject
from PIL import Image
from utils import plot
import uuid


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
        path_to_result1 = "../eval/reltr/0.json"
        self.create_graph(path_to_result1)
        plot.draw_graph(g, "eval/graphs/result1")
        print("Result 1 created! ")

        path_to_result2 = "../eval/reltr/1.json"
        self.create_graph(path_to_result2)
        plot.draw_graph(g, "eval/graphs/result2")
        print("Result 2 created! ")

        path_to_result3 = "../eval/reltr/2.json"
        self.create_graph(path_to_result3)
        plot.draw_graph(g, "eval/graphs/result3")
        print("Result 3 created! ")

        # open image of graph
        im1 = Image.open("../eval/graphs/result1.png")
        im2 = Image.open("../eval/graphs/result2.png")
        im3 = Image.open("../eval/graphs/result3.png")
        im1.show()
        im2.show()
        im3.show()


class TemporalGraph:

    def __init__(self):
        self.g = nx.DiGraph()

    def insert_framegraph(self, framegraph, match_confidence=0.1):
        temporal_nodes = set(self.g.nodes)

        # TODO: better matching algorithm (look into https://en.wikipedia.org/wiki/Assignment_problem)
        for f in framegraph.nodes:
            frame_node = framegraph[f]
            best_match = None
            best_similarity = -1
            for t in temporal_nodes:
                neighbor_matches = 0
                # Count how many neighbours are shared
                for nt in nx.neighbors(self.g, t):
                    for nf in nx.neighbors(framegraph, f):
                        if self.g[nt]["content"].name == framegraph[nf].name:
                            neighbor_matches += 1
                similarity = neighbor_matches / len(nx.neighbors(self.g, t))
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = t
            # Add or update node
            if best_similarity < match_confidence:
                node_identifier = f"{frame_node.name}_{uuid.uuid4()}"
                self.g.add_node(node_identifier, content=frame_node)
            else:
                self.g[t]["content"] = frame_node
            temporal_nodes.remove(t) # once assigned, remove for faster lookup

        for e in framegraph.edges:



if __name__ == "__main__":
    g = FrameGraph(0)
    g.test_frame_graph()

