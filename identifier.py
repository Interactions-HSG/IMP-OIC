from utils.inout import *

# TODO: Think about not returning the target object itself
def get_local_context(target_object, environment, epsilon=0.1):
    """
    Takes a single target object and all the objects in its environment.
    Returns a subset of the environment describing the target object's context
    """
    # Currently, we only look at proximity (box around the target object)
    context = []
    # Proximity box with xmin, ymin, xmax, ymax
    proximity_box = (
        max(target_object.xmin - epsilon, 0),
        max(target_object.ymin - epsilon, 0),
        min(target_object.xmax + epsilon, 1),
        min(target_object.ymax + epsilon, 1)
    )
    for object in environment:
        if object.within(proximity_box):
            context.append(object)
    return context


# TODO: Think about not returning the target triple itself
def get_context_graph(target, environment, epsilon):
    """
    Takes a single target object and all environment triples.
    Returns a sublist of triples that satisfy (target_triple, ..., ...)
    """
    context = []
    for triple in environment:
        # Direct and reflexive match
        if target.approximately_same(triple.object, epsilon) or target.approximately_same(triple.subject, epsilon):
            context.append(triple)
    return context


def test_get_context_graph():
    environment = get_triples("eval/reltr/visualgenome/2361235.json")
    target = environment[5].object # box on desk
    print("Target: ", target)
    context = get_context_graph(target, environment, epsilon=0.3)
    for c in context:
        print(c)


def test_get_local_context():
    environment = get_objects("eval/yolo/2361235.json")
    target = environment[-4] # keyboard
    print("Target: ", target)
    context = get_local_context(target, environment, epsilon=0.1)
    for c in context:
        print(c)


if __name__ == "__main__":
    test_get_context_graph()
    # test_get_local_context()





