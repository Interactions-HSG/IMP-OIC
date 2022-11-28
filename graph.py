import networkx as nx
import json
from structures.scene import SceneObject
import matplotlib.pyplot as plt

class GraphCreator():

    def __init__(self):
        self.g = nx.Graph()

    def create_graph(self, graph_path):
        print("Creating graph...")
        with open(graph_path, "r") as file:
            triples = json.load(file)
            file.close()

        for triple_dict in triples:
            sub = triple_dict["subject"]
            pred = triple_dict["predicate"]
            obj = triple_dict["object"]
            print("Got triple: subj = ", sub, " pred = ", pred, " obj = ", obj)
            subObj = SceneObject(sub["id"], sub["xmin"], sub["ymin"], sub["xmax"], sub["ymax"])
            predicate = pred["id"]
            objObj = SceneObject(obj["id"], obj["xmin"], obj["ymin"], obj["xmax"], obj["ymax"])
            # TODO: somehow check if a 'similar' node already exists ?
            self.g.add_node(subObj)
            self.g.add_node(objObj)
            self.g.add_edge(subObj, objObj, relation=predicate)

    def draw_graph(self):
        nx.draw(self.g, with_labels=True, font_weight='bold')
        plt.savefig("eval/graphs/lookatthisgraph.png")

    def run(self):
        path_to_result = "eval/reltr/2398798.json"
        self.create_graph(path_to_result)
        print(self.g)
        self.draw_graph()



if __name__ == "__main__":
    knowledgeGraph = GraphCreator()
    knowledgeGraph.run()