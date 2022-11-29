import networkx as nx
import json
from structures.scene import SceneObject
import matplotlib.pyplot as plt
from PIL import Image


class FrameGraph():

    def __init__(self):
        self.g = nx.Graph()

    def create_graph(self, graph_path):
        """
            Creates graph for a single frame
        """
        print("Creating graph...")
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

            graph_subj = self.node_in_graph(sub_obj)
            graph_obj = self.node_in_graph(obj_obj)

            # adding nodes and edges gets ignored in graph if already exists so no additional check necessary
            self.g.add_node(graph_subj)
            self.g.add_node(graph_obj)
            self.g.add_edge(graph_subj, graph_obj, relation=predicate)

    def node_in_graph(self, subj):
        """
            Check if node already exists in graph or is sufficiently similar for same frame to identify same objects
            return that node if exists, otherwise the original node
        """
        for node in self.g.nodes:
            if node.name == subj.name and subj.approximately_same(node, 0.3):
                return node
        return subj

    def draw_graph(self):
        pos = nx.spring_layout(self.g, seed=7)

        edge_width = [len(self.g.get_edge_data(u, v)) for u, v in self.g.edges()]
        nx.draw_networkx_edges(self.g, pos, alpha=0.3, width=edge_width, edge_color="m")

        edge_labels = nx.get_edge_attributes(self.g, "relation")
        nx.draw_networkx_edge_labels(self.g, pos, edge_labels)

        nx.draw_networkx_nodes(self.g, pos, node_size=0, node_color="#210070", alpha=0.9)
        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
        nx.draw_networkx_labels(self.g, pos, font_size=14, bbox=label_options)

        ax = plt.gca()
        ax.margins(0.1, 0.05)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig("eval/graphs/lookatthisgraph.png")

    def run(self):
        path_to_result = "eval/reltr/2398798.json"
        self.create_graph(path_to_result)
        print("Graph created!")
        print(self.g)
        self.draw_graph()

        # open image of graph
        im = Image.open("eval/graphs/lookatthisgraph.png")
        im.show()


if __name__ == "__main__":
    knowledgeGraph = FrameGraph()
    knowledgeGraph.run()
