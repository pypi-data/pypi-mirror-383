from pyrbd3 import read_graph, evaluate_availability

topo = "Germany_17"
G, _, _ = read_graph(f"topologies/{topo}", topo)

node_prob = {node: 0.9 for node in G.nodes()}

src, dst = 0, 1

availability = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="sdp")

print(f"System availability from {src} to {dst} in {topo}: {availability:.6f}")