import json

from structures.scene import *

def get_triples(graph_path):
    """
    Complete import of a graph created with RelTR
    """
    triples_read = []
    with open(graph_path, "r") as file:
        triples = json.load(file)
        file.close()

    for triple_dict in triples:
        subject = triple_dict["subject"]
        predicate = triple_dict["predicate"]
        object = triple_dict["object"]
        triple = SceneTriple(subject["id"], subject["xmin"], subject["ymin"], subject["xmax"], subject["ymax"],
                             predicate["id"],
                             object["id"], object["xmin"], object["ymin"], object["xmax"], object["ymax"])
        triples_read.append(triple)
    print(f"Loaded {len(triples_read)} objects from {graph_path}")
    return triples_read
    
def clean_img_list(l):
    l1 = []
    for el in l:
        if el[-3:] in ["jpg", "png"] or el[-4:] == "jpeg":
            l1.append(el)
    return l1
    
def clean_json_list(l):
    l1 = []
    for el in l:
        if el[-4:] == "json":
            l1.append(el)
    return l1

if __name__ == "__main__":
    pass