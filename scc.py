import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph (DiGraph)
G = nx.DiGraph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (4, 5)])

# Get the strongly connected components
strong_components = list(nx.strongly_connected_components(G))

# Print the sizes of each component
for component in sorted(strong_components, key=len, reverse=True):
    print(f"Component size: {len(component)}")

# If you only want the largest component, you can use max
largest_component = max(strong_components, key=len)
print(f"Largest component size: {len(largest_component)}")

nx.draw(G, with_labels=True)
plt.show()