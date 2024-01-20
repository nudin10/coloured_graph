import networkx as nx
import matplotlib.pyplot as plt


all_nodes = [i + 1 for i in range(10)]
g = nx.complete_graph(all_nodes)


cg = nx.Graph()
nodes = [
    (1, 4),
    (1, 8),
    (1, 7),
    (1, 5),
    (2, 3),
    (2, 8),
    (2, 9),
    (3, 6),
    (3, 7),
    (3, 9),
    (3, 10),
    (4, 5),
    (4, 6),
    (4, 8),
    (4, 10),
    (5, 7),
    (5, 8),
    (6, 7),
    (6, 10),
    (7, 10),
    (8, 9),
]

supervisors = {
    1: [1, 2],
    2: [1, 3],
    3: [1, 4],
    4: [2, 3],
    5: [2, 5],
    6: [4, 5],
    7: [5, 6],
    8: [2, 6],
    9: [1, 2],
    10: [3, 6],
}

panels = {
    1: [3, 4],
    2: [5, 6],
    3: [6, 2],
    4: [1, 4],
    5: [4, 3],
    6: [2, 1],
    7: [3, 2],
    8: [4, 5],
    9: [5, 6],
    10: [1, 2],
}

cg.add_edges_from(nodes)
# d = nx.coloring.greedy_color(cg, strategy="largest_first")
nx.set_node_attributes(cg, supervisors, "supervisors")
nx.set_node_attributes(cg, panels, "panels")
pos = nx.spring_layout(cg, seed=42)
nx.draw(cg, pos, with_labels=True)
plt.title("Graph")
plt.show()