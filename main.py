import identifier
import parser
from structures.identity import Fingerprint


def main():
    templates, templates_classes = import_fingerprints("templates/obj_templates.json")
    template_similarity_thresh = 0.5

    matches = []
    # TODO: while(True) loop
    # TODO: Get data from image
    objects = import_objects("eval/yolo/2361235.json")

    for object in objects:
        if object.name in templates_classes:  # only look at objects whose class is in a template
            context = identifier.get_local_context(object, objects, epsilon=0.1)
            obj_fingerprint = Fingerprint(object, context, "")
            for template in templates:
                if template.similarity(obj_fingerprint) > template_similarity_thresh:
                    matches.append(template)
    for match in matches:
        print(match)


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


def import_objects(objects_path):
    """"
    Imports objects from image classifier file
    """
    objects = parser.parse_objects("eval/yolo/2361235.json")
    print(f"Loaded {len(objects)} objects from {objects_path}")
    return objects


if __name__ == "__main__":
    main()
