import json

from structures.identity import Fingerprint
from structures.scene import *

def parse_triples(graph_path):
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
    return triples_read


def parse_objects(objects_path):
    """
    Import of objects created with yolo v4 and --out option
    """
    objects = [] # objects are NOT unique, therefore no set
    with open(objects_path, "r") as file:
        frames = json.load(file) # frames is a list of frames
        file.close()

    for frame in frames:
        obj_dicts = frame["objects"]
        for obj_dict in obj_dicts:
            name = obj_dict["name"]
            coords = obj_dict["relative_coordinates"]
            objects.append(SceneObject.from_centre(name, coords["center_x"], coords["center_y"], coords["width"], coords["height"]))
    return objects

def parse_triple_templates(template_path):
    """
    Imports fingerprint templates from file
    """
    fingerprints = []
    with open(template_path, "r") as file:
        templates = json.load(file)
        file.close()

    for template in templates:
        subject = SceneObject.from_desc(template["subject"])
        anchors = []
        for a in template["anchors"]:
            anchors.append(SceneTriple.from_desc(a["subject"], a["predicate"], a["object"]))
        identifier = SceneObject.from_desc(template["identifier"])
        fingerprints.append(Fingerprint(subject, anchors, identifier))
    return fingerprints

def parse_object_templates(template_path):
    """
    Imports fingerprint templates from file
    """
    fingerprints = []
    with open(template_path, "r") as file:
        templates = json.load(file)
        file.close()

    for template in templates:
        subject = SceneObject.from_desc(template["subject"])
        anchors = []
        for a in template["anchors"]:
            anchors.append(SceneObject.from_desc(a))
        identifier = SceneObject.from_desc(template["identifier"])
        fingerprints.append(Fingerprint(subject, anchors, identifier))
    return fingerprints

if __name__ == "__main__":
    # objects = parse_objects("eval/yolo/2361235.json")
    # for o in objects:
    #     print(o)
    #
    # triples = parse_triples("eval/reltr/2361235.json")
    # for t in triples:
    #     print(t)

    fingerprints = parse_triple_templates("templates/triple_templates.json")
    for f in fingerprints:
        print(f)

    fingerprints = parse_object_templates("templates/obj_templates.json")
    for f in fingerprints:
        print(f)