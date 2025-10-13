# PyRBD3
Fast and lightweight Reliability Block Diagram (RBD) evaluation library, powered by modern C++ and pybind11.
Provides high-performance algorithms for minimal cut sets, path sets, and system availability computation.

## Installation

Precompiled binary wheels are available for Linux:
```bash
pip install pyrbd3
```

That’s it — no compiler setup or manual build steps are required.
If you prefer a clean environment:
```bash
conda create -n pyrbd3 python=3.10
conda activate pyrbd3
pip install pyrbd3
```

## Quick Example

```python
from pyrbd3 import read_graph, evaluate_availability

topo = "Germany_17"
G, _, _ = read_graph(f"topologies/{topo}", topo)

node_prob = {node: 0.9 for node in G.nodes()}

src, dst = 0, 1

availability = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="sdp")

print(f"Availability {availability}")
```

## Topology Reference
**Germany_17**: [SNDlib 1.0-survivable network design library](https://sndlib.put.poznan.pl/home.action)
