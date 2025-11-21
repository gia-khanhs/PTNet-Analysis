# PTNet-Analysis
A recursive link to the repo: [PTNet-Analysis](https://github.com/gia-khanhs/PTNet-Analysis)

This is my own implementation of the research paper [A comparative study of topological analysis and temporal network analysis of a public transport system](https://www.sciencedirect.com/science/article/pii/S204604302100037X)

Read more about L-space graph: [Statistical analysis of 22 public transport networks in Poland](https://arxiv.org/pdf/physics/0506074)

## Table of Contents
- [0. Overview](#0-overview)
  - [0.1 Topological graph stats](#01-topological-graph-stats)
- [1. Technical details](#1-technical-details)
  - [1.1 Included libraries]
  - [1.2 The method to approximate the geographical distance](#12-the-method-to-approximate-the-geographical-distance)

## 0. Overview:

### 0.1 Topological graph stats:
- The code to build, save and load the code can be found and run in "topoDataIO.py".
- The graph is a single graph (If there are multiple edges from $u$ to $v$, the one with the least travel time will overwrite others), saved in "topoGraph.json".
- It has 4355 nodes / 5425 edges (vs. paper 4350/5397):
  - Note that this is the number of edges in connecting consecutive stops in a route (edges within walking distance not considered), counted for the sake of comparision with the paper. In fact, the saved graph has many more edges (18723).
  - The nodes in the saved file are numbered from 1 to whatever the number of nodes is, with an extra at the beginning just for ease of assigning the node ID with its relevant data.
  - The edges are saved using an adjacency list.
- A possible explanation for the difference: With my code version on 9th November, I used different StationId to mark distinct nodes, resulting in 4370 nodes, while using the Address results in 4355. This means that the author may have another way of choosing how to merge nodes. As a result, more edges will be created instead of being overwritten, creating some more of them.

| Build time & memory:                                       |
|  Action(s) \ Stats | Time (seconds)  | Mem / Peak mem (MB) |
| :----------------- | :-------------: | :-----------------: |
| **Build**          | 72.011          | 6.97 / 10.49        |
| **Build + Save**   | 145.754         | 0.27 / 11.57        |
| **Load**           | 0.228           | 5.77 / 19.39        |
- Disk usage: 3.75 MB (To save the topological graph).
## 1. Technical details:

### 1.1 Included libraries:
- To make the coding process easier, these libraries were used: geojson, turfpy.
- Installation: 
```pip install geojson```
```pip install turfpy```

### 1.2 The method to approximate the geographical distance:
- The idea is to create a 3D point ($L_{i}$) for each geographical location:
- Assume Earth is a sphere in the 3D space, with the origin O located at the middle of the sphere. The latitude ($lat$) will be the angle between Oz and the secant line ($sc$) of O and $L_{i}$, the longitude ($lng$) will be the angle between Ox and the projection of ($sc$) on Oxy (lets call the length of the projection $p$).
- Knowing these, we can calculate the 3D position as follow:
Let $L_{i}(x, y, z)$
<p align="center"> $z = R_{Earth} * cos(lat)$ </p>
<p align="center"> $p = \sqrt{R_{Earth}^2 - z^2} = R_{Earth} * sin(lat)$ </p>
<p align="center"> $x = p * cos(lng)$ </p>
<p align="center"> $y = p * sin(lng)$ </p>
Simplifying these, we get:
<p align="center"> $x = R_{Earth} * sin(lat) * cos(lng)$ </p>
<p align="center"> $y = R_{Earth} * sin(lat) * sin(lng)$ </p>
<p align="center"> $z = R_{Earth} * cos(lat)$ </p>

- Having the 3D coordinates, we can calculate the angle between two points A and B in the 3D space using dot product:
<p align="center"> $cos(\theta) = \frac{\vec{OA}.\vec{OB}}{|OA|.|OB|}$ </p>
<p align="center"> $\iff \theta = cos^{-1}(\frac{\vec{OA}.\vec{OB}}{|OA|.|OB|})$ </p>

- This then can be used to calculate the length of the arc between those two points (which is the approximation of the geographical distance):
<p align="center"> $d = \frac{\theta}{2\pi}.R_{Earth}$ </p>