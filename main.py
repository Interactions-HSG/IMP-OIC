import identifier
import parser
from structures.identity import Fingerprint
from utils.simulation import FrameGenerator


def main():
    templates, templates_classes = import_fingerprints("templates/obj_templates.json")
    template_similarity_thresh = 0.5

    while(True):
        c = input("\nPress q to leave or enter to identify")

        if c == "q":
            break

        matches = []
        nonmatches = []
        # TODO: Get data from image
        objects = import_objects("eval/yolo/2361235.json")

        for object in objects:
            context = identifier.get_local_context(object, objects, epsilon=0.1)
            obj_fingerprint = Fingerprint(object, context, "")
            if object.name in templates_classes:  # only look at objects whose class is in a template
                for template in templates:
                    if template.similarity(obj_fingerprint) > template_similarity_thresh:
                        matches.append(template)
            else:
                nonmatches.append(obj_fingerprint)

        print(f"\nFound {len(matches)} matches in scene:")
        for match in matches:
            print(match)

        print(f"\nFound {len(nonmatches)} objects not identified:")
        for n, nonmatch in enumerate(nonmatches):
            print(f"{n}: {nonmatch}")

        while(True):
            n = input("\nType the object's number you want to identify or skip with s\n")
            if n == "s":
                break
            n = int(n)
            new_fingerprint = nonmatches[n]
            object_id = input(f"\nWhat is the {new_fingerprint.subject.name}s identifier?\n")
            new_fingerprint.identifier = object_id
            templates_classes.add(new_fingerprint.subject.name)
            templates.append(new_fingerprint)

def mainframes():
    templates, templates_classes = import_fingerprints("templates/obj_templates.json")
    template_similarity_thresh = 0.5

    tracked = []

    generator = FrameGenerator(sample=1)
    # while we receive frames
    while(generator.has):



def import_fingerprints(fingerprints_path):
    """
    Import user-defined fingerprints from a file
    """
    fingerprints = parser.parse_object_templates(fingerprints_path)
    classes = set()
    for f in fingerprints:
        classes.add(f.subject.name)
    print(f"Loaded {len(fingerprints)} from {fingerprints_path}")
    return fingerprints, classes

def export_fingerprints(fingerprints, fingerprints_path):
    """
    Exports learned objects with identifier into file
    """
    with open(fingerprints_path, "w") as file:
        for f in fingerprints:
            pass
    

def import_objects(objects_path):
    """"
    Imports objects from image classifier file
    """
    objects = parser.parse_objects(objects_path)
    print(f"Loaded {len(objects)} objects from {objects_path}")
    return objects
    


if __name__ == "__main__":
    main()
