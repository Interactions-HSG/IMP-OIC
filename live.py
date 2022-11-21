from utils.inout import *
from utils.simulation import *
import identifier

def main():
    templates = get_triple_templates("templates/glass.json")
    templates_classes = get_fingerprint_classes(templates)
    fingerprints = [templates]  # List of fingerprints, one per frame
    template_similarity_thresh = 0.1

    generator = FrameGenerator() # Substitute for camera, reltr combo
    frame_counter = 1
    # while we receive frames
    while(generator.has_next()):
        # Get offline classification result
        path_to_result = generator.next()
        triples = get_triples(path_to_result)
        
        matches = []

        for triple in triples:
            context = identifier.get_context_graph(triple.subject, triples, epsilon=0.3)
            fingerprint = Fingerprint(triple.subject, context, "")
            reflexive_fingerprint = Fingerprint(triple.object, context, "")
            
            if triple.subject.name in templates_classes:  # only look at subjects whose class is in a template
                for template in fingerprints[frame_counter-1]: # compare with previous fingerprints
                    similarity_score = template.triple_similarity(fingerprint, epsilon=0.1) # TODO: split similarity into spatial and logical
                    if similarity_score > template_similarity_thresh: # TODO: think about using prior probabilities from previous frame
                        print(f"Matched {template} with {fingerprint} on similarity {similarity_score}")
                        matches.append(fingerprint)
            elif triple.object.name in templates_classes: # look at objects whose class is in a template, as triples can be reflexive
                for template in fingerprints[frame_counter-1]:
                    similarity_score = template.triple_similarity(reflexive_fingerprint, epsilon=0.1) # TODO: split similarity into spatial and logical
                    if similarity_score > template_similarity_thresh: # TODO: think about using prior probabilities from previous frame
                        print(f"Matched {template} with {reflexive_fingerprint} on similarity {similarity_score}")
                        matches.append(reflexive_fingerprint)
        
        fingerprints.append(matches)
        frame_counter += 1
        inp = input("Press enter to move to next frame\n")


def print_fingerprints(fingerprints):
    for i, f in enumerate(fingerprints):
        print(f"Frame {i}:")
        print("".join(f))
        print("--------------")


if __name__ == "__main__":
    main()