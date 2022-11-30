import networkx as nx
import matplotlib.pyplot as plt


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