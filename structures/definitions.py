import networkx as nx

elist = [('hand', 'arm', 0.5), ('hand', 'person', 0.2), ('hand', 'finger', 0.6), ('glass', 'cup', 0.8),
         ('glass', 'cup', 0.8), ('person', 'woman', 0.8), ('person', 'man', 0.8), ('mouth', 'person', 0.4),
         ('mouth', 'woman', 0.4), ('mouth', 'man', 0.4), ('woman', 'girl', 0.9), ('man', 'boy', 0.9),
         ('boy', 'person', 0.9), ('girl', 'person', 0.9)]
SIMILAR_NAMES = nx.Graph()
SIMILAR_NAMES.add_weighted_edges_from(elist)


def name_similarity(a, b):
    """
    Returns graph with name similarities for fuzzy matching
    """
    if a == b:
        return 1
    else:
        if (a, b) in SIMILAR_NAMES.edges:
            return SIMILAR_NAMES[a][b]["weight"]
        else:
            return 0
