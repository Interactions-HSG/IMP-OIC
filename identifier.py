import parser

# TODO: Think about not returning the target object itself
def get_local_context(target_object, environment):
    """
    Takes a single target object and all the objects in its environment.
    Returns a subset of the environment describing the target object's context
    """
    # Currently, we only look at proximity (box around the target object)
    context = []
    epsilon = 0.1
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
def get_context_graph(target_object, environment):
    """
    Takes a single target object and all environment triples.
    Returns a sublist of triples that satisfy (target_triple, ..., ...)
    """
    context = []
    epsilon = 0.1
    for triple in environment:
        # Direct match
        if target_object.approximately_same(triple.subject, epsilon):
            context.append(triple)
    return context


def test_get_context_graph():
    environment = parser.parse_triples("eval/reltr/2361235.json")
    target = environment[5].subject # paper on desk
    context = get_context_graph(target, environment)
    for c in context:
        print(c)


def test_get_local_context():
    environment = parser.parse_objects("eval/yolo/2361235.json")
    target = environment[-4] # keyboard
    context = get_local_context(target, environment)
    for c in context:
        print(c)


if __name__ == "__main__":
    # test_get_context_graph()
    test_get_local_context()





