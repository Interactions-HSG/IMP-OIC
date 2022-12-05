import networkx as nx
import matplotlib.pyplot as plt
from utils.inout import get_triples


def draw_graph(g, path):
    fig = plt.figure(1, figsize=(10, 5))
    pos = nx.spring_layout(g, seed=7)

    edge_width = [len(g.get_edge_data(u, v)) for u, v in g.edges()]
    nx.draw_networkx_edges(g, pos, alpha=0.3, width=edge_width, edge_color="m")

    edge_labels = nx.get_edge_attributes(g, "relation")
    nx.draw_networkx_edge_labels(g, pos, edge_labels)

    nx.draw_networkx_nodes(g, pos, node_size=0, node_color="#210070", alpha=0.9)
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx_labels(g, pos, font_size=14, bbox=label_options)

    ax = plt.gca()
    ax.margins(0.1, 0.05)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path + ".png")


def draw_reltr_image(img_path, graph_path):
    triples = get_triples(graph_path)
    fig, ax = plt.subplots()
    im = plt.imread(img_path)
    ax.imshow(im)
    for triple in triples:
        o = triple.object
        s = triple.subject
        oxcentre = o.xmin + (o.xmax - o.xmin) / 2
        oycentre = o.ymin + (o.ymax - o.ymin) / 2
        sxcentre = s.xmin + (s.xmax - s.xmin) / 2
        sycentre = s.ymin + (s.ymax - s.ymin) / 2
        xlinecentre = oxcentre + (sxcentre - oxcentre) / 2
        ylinecentre = oycentre + (sycentre - oycentre) / 2
        ax.add_patch(plt.Rectangle((s.xmin, s.ymin), s.xmax - s.xmin, s.ymax - s.ymin,
                                   fill=False, color='blue', linewidth=2.5))
        ax.add_patch(plt.Rectangle((o.xmin, o.ymin), o.xmax - o.xmin, o.ymax - o.ymin,
                                   fill=False, color='orange', linewidth=2.5))
        ax.annotate(triple.subject, (s.xmin, s.ymin), color="white")
        ax.annotate(triple.object, (o.xmin, o.ymin), color="white")
        # ax.add_patch(plt.Arrow((sxcentre, sycentre), (oxcentre, oycentre), color="red"))
        ax.annotate(triple.predicate, (xlinecentre, ylinecentre), color="white")
    plt.show(block=False)
    plt.show()
