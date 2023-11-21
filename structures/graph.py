from types import GeneratorType
import networkx as nx
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from PIL import Image
import uuid
import numpy as np
import time
from collections import defaultdict
from structures.scene import SceneObject

import utils.plot
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
        similarity_tol = 0.5

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
            obj_obj = SceneObject(obj["id"], obj["xmin"], obj["ymin"], obj["xmax"], obj["ymax"])
            predicate = pred["id"]

            # Get the closest nodes and add them to the graph
            graph_subj = self.get_closest_node(sub_obj, epsilon=similarity_tol)
            graph_obj = self.get_closest_node(obj_obj, epsilon=similarity_tol)

            # Set the positions in the nodes
            graph_subj.pos = sub_obj.pos
            graph_obj.pos = obj_obj.pos

            # Add nodes and edges
            self.g.add_node(graph_subj, content=sub_obj)
            self.g.add_node(graph_obj, content=obj_obj)
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
        self.g = nx.MultiDiGraph()
        self.frame_ids = []
        self.out_of_frame = set()
        self.leaf_node_id = {}
        

    def calculate_similarity(self, alpha, f, t, framegraph):
        """
        Calculate a similarity score between elements based on neighbor matches, bounding box similarity, and name similarity.
    
        Parameters:
        alpha (float): The weighting factor for neighbor similarity (0 <= alpha <= 1).
        f: The source element to calculate similarity from.
        t: The target element to calculate similarity to.
        framegraph: A graph representing the frames.
    
        Returns:
        float: The calculated similarity score.
        """
        
        # Initialize neighbor similarity and neighbor matches count
        neigh_similarity = 0
        neighbor_matches = 0
        # Get the number of neighbors for the target element
        n_neighbours = len(self.g[t])
        # Calculate neighbor similarity
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
        
        # Calculate the final similarity score 
        similarity = (alpha * neigh_similarity + (1-alpha) * spat_similarity + n_similarity) / 2
        return similarity


    def insert_framegraph(self, framegraph, alpha, min_assignment_conf, framegraph_pre, verbose=False):
        """
            Update the graph by incorporating information from the provided framegraph.
        
            Parameters:
            framegraph: A framegraph containing nodes and their relations.
            alpha (float): The weighting factor for neighbor similarity (0 <= alpha <= 1).
            min_assignment_conf (float): Minimum similarity threshold for assigning a node.
            verbose (bool, optional): Print additional information if True. Default is False.
        """
        # Get nodes from the framegraph
        fg_nodes = framegraph.g.nodes
        # Update the set of nodes in the graph
        G = set(self.g.nodes)
         #   G.update(self.out_of_frame)
        relations={'has', 'attached to', 'covering', 'growing on', 'hanging from', 'made of', 'on', 'painted on', 'part of', 'sitting on', 'standing on', 'wearing', 'wears'}
        update_nodes = set()   # Set with nodes that need to be updated
        Bestmatch = {}
        for f in fg_nodes:
            max_similarity = -1
            # Calculate similarity for each node in the graph
            for g in G:
                #print(g)
                similarity = self.calculate_similarity(alpha, f, g, framegraph)
                if max_similarity<similarity:
                    max_similarity=similarity
                    #print(g)
                    if g not in Bestmatch:
                        Bestmatch[f]=g            # Assign a node if similarity exceeds the minimum assignment confidence
            if max_similarity > min_assignment_conf:
                cui = self.g.nodes[Bestmatch[f]]["content"].get_cuid()
                framegraph.g.nodes[f]["content"].cuid=cui
                content=framegraph.g.nodes[f]["content"]
                self.g.nodes[Bestmatch[f]]["content"] = content
                update_nodes.add(cui)
                self.leaf_node_id[str(cui)] = f
            else:
                flag=False
                if framegraph_pre != None:
                    edges = list(framegraph.g.out_edges(f, data=True)) + list(framegraph.g.in_edges(f, data=True))
                    for node1, node2, data in edges:
                        if data["relation"] in relations:
                            if framegraph.g.nodes[node1]["content"].cuid in self.g.nodes():# and self.leaf_node_id[node1.cuid] in self.g.nodes():
                                if node2.name==self.g.nodes[Bestmatch[node2]]["content"].name:
                                    cui = self.g.nodes[Bestmatch[f]]["content"].get_cuid()
                                    framegraph.g.nodes[f]["content"].cuid=cui
                                    content=framegraph.g.nodes[f]["content"]
                                    self.g.nodes[Bestmatch[f]]["content"] = content
                                    update_nodes.add(cui)
                                    self.leaf_node_id[str(cui)] = f
                                    flag=True
                                    break
                            elif framegraph.g.nodes[node2]["content"].cuid in self.g.nodes():
                                if node1.name==self.g.nodes[Bestmatch[node1]]["content"].name:
                                    cui = self.g.nodes[Bestmatch[f]]["content"].get_cuid()
                                    framegraph.g.nodes[f]["content"].cuid=cui
                                    content=framegraph.g.nodes[f]["content"]
                                    self.g.nodes[Bestmatch[f]]["content"] = content
                                    update_nodes.add(cui)
                                    self.leaf_node_id[str(cui)] = f
                                    flag=True
                                    break
                    if flag:
                        for node1, node2, data in framegraph.g.edges(f, data=True):
                            if data["relation"] in relations:
                                if framegraph.g.nodes[node2]["content"].get_cuid() in self.g.nodes(): 
                                    if node1.name==self.g.nodes[Bestmatch[node1]]["content"].name:
                                        cui=self.g.nodes[Bestmatch[node1]]["content"].get_cuid()
                                        framegraph.g.nodes[node1]["content"].cuid = cui
                                        update_nodes.add(cui)
                                        self.leaf_node_id[str(cui)] = node1
                                elif framegraph.g.nodes[node1]["content"].get_cuid() in self.g.nodes():
                                    if node2 in Bestmatch.keys():
                                        if node2.name==self.g.nodes[Bestmatch[node2]]["content"].name:
                                            cui=self.g.nodes[Bestmatch[node2]]["content"].get_cuid()
                                            framegraph.g.nodes[node2]["content"].cuid = cui
                                            update_nodes.add(cui)
                                            self.leaf_node_id[str(cui)] = node2
                        continue
                # Generate a unique identifier for the leaf node
                print(flag)
                CUID = str(uuid.uuid4())[0:4]
                unique_node_id = f"{f}_{CUID}"
                
                
                framegraph.g.nodes[f]["content"].cuid=unique_node_id
                content=framegraph.g.nodes[f]["content"]
                  
                # Add the node with its ID to the graph
                self.g.add_node(unique_node_id, appearance_time=framegraph.frame_id)
                nx.set_node_attributes(self.g, {unique_node_id: content}, 'content')

                self.leaf_node_id[unique_node_id] = f
                update_nodes.add(unique_node_id)
                
                
        # Update edges
        for u in update_nodes:
            edges = list(framegraph.g.out_edges(self.leaf_node_id[u]))
            time = framegraph.frame_id
            for edge in edges:
                n0, n1=edge
                relation = framegraph.g[n0][n1]['relation']
                node1_cuid = framegraph.g.nodes[n0]["content"].cuid
                node2_cuid = framegraph.g.nodes[n1]["content"].cuid    
                if not self.g.has_edge(node1_cuid, node2_cuid) or (list(self.g[node1_cuid][node2_cuid].values())[-1]["relation"]==relation and int(list(self.g[node1_cuid][node2_cuid].values())[-1]["lastPresence"]<int(framegraph.frame_id-1))):
                    self.g.add_edge(node1_cuid, node2_cuid, lastPresence= time, appearance_time = time, relation=relation )
            edges_to_add = set()       
            edges=self.g.out_edges(u)
            for edge in edges:
                n0, n1=edge
                if framegraph.g.has_edge(self.leaf_node_id[n0], self.leaf_node_id[n1]):
                    relation = framegraph.g[self.leaf_node_id[n0]][self.leaf_node_id[n1]]['relation']  
                    keys_to_modify = set()
                    keys=self.g[n0][n1]
                    for key in keys:
                        edge_data = self.g[n0][n1][key]
                        if edge_data["relation"]==relation and int(edge_data["lastPresence"])==int(framegraph.frame_id-1):
                            keys_to_modify.add(key)
                            break
                    for key in keys_to_modify:
                        self.g[n0][n1][key]["lastPresence"] = framegraph.frame_id
                    
            for n0, n1, relation in edges_to_add: 
                self.g.add_edge(n0, n1, lastPresence= time, appearance_time = time, relation=relation)
            
            
            

             
       
                
    def to_text(self, export_path):
        """
        Export a textual representation of the scene based on edge         
        appearance and disappearance times.
    
        Parameters:
        export_path (str): The file path to save the exported text.
        """
    
        timestep=1 #in seconds
        timepoint=0
        G=self.g    #Graph
        
        # Sort edges based on appearance and disappearance times
        sorted_edges_appearance = list(sorted(G.edges(data=True), key=lambda x: x[2]['appearance_time']))
        sorted_edges_disappearance = list(sorted(G.edges(data=True), key=lambda x: x[2]['lastPresence']))

        with open(export_path, 'w') as file:
                file.write(f"At the beginning of the scene:\n")
                while True:
                    sorted_edges_disappearance_rem = []
                    sorted_edges_appearance_rem = []
                    
                    # Process edges based on appearance time
                    for edge in sorted_edges_appearance:
                        n1, n2, data = edge
                        appearance_time = data.get('appearance_time')
                        #print("AppTime:"+str(appearance_time))
                        if appearance_time == timepoint:
                            relation=data.get('relation')
                            file.write(f"{n1} {relation} {n2}\n")
                            sorted_edges_appearance_rem.append(edge)
                        else:
                            break
                        
                    # Process edges based on disappearance time
                    
                    for edge in sorted_edges_disappearance:
                        n1, n2, data = edge
                        disappearance_time = data.get('lastPresence')
                        #print("DisTime:"+ str(disappearance_time))
                        if disappearance_time == timepoint:
                            relation=data.get('relation', None)
                            #file.write(f"{n1} {relation} {n2} is not longer actual.\n")   
                            sorted_edges_disappearance_rem.append(edge)
                        else:                         
                            break
                    
                    # Remove processed edges
                    sorted_edges_appearance = [item for item in sorted_edges_appearance if item not in sorted_edges_appearance_rem]
                    sorted_edges_disappearance = [item for item in sorted_edges_disappearance if item not in sorted_edges_disappearance_rem] 

                    if len(sorted_edges_appearance)==0 and len(sorted_edges_disappearance)==0:
                        file.write(f"The scene ends \n")
                        file.close()
                        break
                    timepoint+=1
                    file.write(f"After {timepoint*timestep} seconds:\n")

    def to_frame_plot(self, img_path, export_path, framegraph):
        """
        Draws, with the addition of the image, the current framegraph as overlay
        """
        fig, ax = plt.subplots()
        im = plt.imread(img_path)
        ax.imshow(im)
        ax.set_axis_off()
        
        for n in framegraph.g.nodes:
            o = framegraph.g.nodes[n]["content"]
            oxcentre = o.xmin + (o.xmax - o.xmin) / 2
            oycentre = o.ymin + (o.ymax - o.ymin) / 2
            ax.add_patch(plt.Rectangle((o.xmin, o.ymin), o.xmax - o.xmin, o.ymax - o.ymin,
                                       fill=False, color="blue", linewidth=2.5))
            cuid = framegraph.g.nodes[n]["content"].get_cuid()
            ax.annotate(cuid, (o.xmin, o.ymin), color="white")
        plt.savefig(export_path + ".png", dpi=200, bbox_inches="tight")

    def to_plot(self, export_path):
        """
        Plots the temporal graph in 3d space. Works best for < 5 frames.
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

        if len(self.frame_ids) > 10:
            plot_ids = []
            for i in range(self.frame_ids[0], len(self.frame_ids), 10):
                plot_ids.append(self.frame_ids[i])
        else:
            plot_ids = self.frame_ids

        for i, f in enumerate(plot_ids):
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

    tg.to_plot("temporal.png")
    
def test_temporal_graph_to_frame_plot():
    fg1 = FrameGraph(1)
    fg1.create_graph("../eval/reltr/airport/0.json")

    tg = TemporalGraph()
    tg.insert_framegraph(fg1, 0.1, 0.3, verbose=True)

    tg.to_frame_plot("../eval/img/airport/4.jpg", "frameplot")

if __name__ == "__main__":
    # g = FrameGraph(0)
    # g.test_frame_graph()
    # test_temporal_graph()
    # test_temporal_graph_to_text()
    # test_temporal_graph_to_plot()
    test_temporal_graph_to_frame_plot()