import networkx as nx
import numpy as np
from typing import Dict
import matplotlib.pyplot as plt

from NE.epsilon.weighted_search import Node, build_weight_map_from_graph

def draw_graph(graph: Dict[int, Node]):
    G = nx.Graph()

    # Add nodes
    for node_id in graph:
        G.add_node(node_id)

    # Add edges
    for node_id in graph:
        for edge_node in graph[node_id].edges:
            G.add_edge(node_id, edge_node)


    c = nx.community.naive_greedy_modularity_communities(G)
    e = nx.eigenvector_centrality(G)

    max_centrality = -9999.0
    max_centrality_node = None

    for node_id in e:
        if e[node_id] > max_centrality:
            max_centrality = e[node_id]
            max_centrality_node = node_id

    communities = []
    for community in c:
        if max_centrality_node not in community:
            temp_community = list(community)
            temp_community.append(max_centrality_node)
            communities.append(temp_community)

    print(communities)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()
