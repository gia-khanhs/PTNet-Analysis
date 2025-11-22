# PTNet-Analysis
A recursive link to the repo: [PTNet-Analysis](https://github.com/gia-khanhs/PTNet-Analysis)

This is my own implementation of the research paper [A comparative study of topological analysis and temporal network analysis of a public transport system](https://www.sciencedirect.com/science/article/pii/S204604302100037X)

Read more about L-space graph: [Statistical analysis of 22 public transport networks in Poland](https://arxiv.org/pdf/physics/0506074)

- To make the coding process easier, these libraries were used: turfpy (to work with geographical information).
- Installation: 
```pip install turfpy geojson```

## Table of Contents
- [0. Overview](#0-overview)
  - [0.1 Topological graph stats](#01-topological-graph-stats)
- [1. Technical details](#1-technical-details)
  - [1.1 The method to approximate the geographical distance](#11-the-method-to-approximate-the-geographical-distance)

## 0. Overview:

### 0.1 Topological graph stats:
- With 4 routes removed (61-4, 61-7, 70-5, 72-1), the L-space graph has 4342 nodes / 5372 edges (vs. paper 4350/5397):
  - When edges between nodes within walking distance are added, and any edge from $u$ to $v$ is the optimised one (the smallest travel time between consecutive stops or by walking), the graph is a single graph with 18753 edges.
  - The nodes in the saved file are numbered from 1 to whatever the number of nodes is, with an extra at the beginning just for ease of assigning the node ID with its relevant data.
  - The edges are saved using an adjacency list.
  - The weights of each edge include: distance and travel time (first the distance $d$ between two consecutive stops in a route is calculated, and the travel time will be approximated by $t = \frac{d}{\sum{d}} * \sum{t}$, where $\sum{d}$ and $\sum{t}$ are the total travel distance and time of the bus route respectively).

|  Action(s) \ Stats | Time (seconds)  | Mem / Peak mem (MB) |
| :----------------- | :-------------: | :-----------------: |
| **Build**          | 192.107         | 8.13 / 8.23         |
| **Build + Save**   | 199.855         | 0.14 / 12.54        |
| **Load**           | 0.256           | 5.87 / 19.94        |
- Disk usage: 3.86 MB (To save the topological graph in "saves/topoGraph.json").

- Resources taken to produce "saves/table4.json":
  - Time elapsed: 431.142 s
  - Current memory usage: 0.26 MB; Peak: 1.63 MB
