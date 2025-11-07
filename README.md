# PTNet-Analysis
This is my own implementation of the research paper "A comparative study of topological analysis and temporal network analysis of a public transport system"!

Link to the paper: https://www.sciencedirect.com/science/article/pii/S204604302100037X

Read more about L-space graph: https://arxiv.org/pdf/physics/0506074

## Some notes on my implementation:

### Graph comparision with the paper:
- My graph is a directed single graph. Between stop pairs in walk distance, an edge will be created, and if there is already one (in a bus route), it will be overwritten so that the time weight is minimum.
- My topological graph has 4370 nodes and 5442 edges (without taking edges between stop pair in walk distance into consideration), while the author's has 4350 nodes and 5397.

### Resources taken to build the graph:
- Time elapsed: 199.307 s
- Current memory usage: 5.79 MB; Peak: 6.24 MB

### Resources taken to build and save the graph:
- Time elapsed: 142.263 s
- Current memory usage: 10.24 MB; Peak: 10.30 MB

## Technical details:

### 1. The method to approximate the geographical distance:
- The idea is to create a 3D point for each geographical location ($L_{i}$):
- Assume Earth is a sphere in the 3D space, with the origin O located at the middle of the sphere. The latitude will be the angle between Oz and the secant line (sc) of O and $L_{i}$, the longitude will be the angle between Ox and the projection of (sc) on Oxy (lets call the projection pj).
- Knowing these, we can calculate the 3D position as follow:
Let $L_{i}(x, y, z)$
<p align="center"> $z = R_{Earth} * cos(lat) \end{center}$ </p>
<p align="center"> $pj = \sqrt{R_{Earth}² - z²} = R_{Earth} * sin(lat)$ </p>
<p align="center"> $x = pj * cos(lng)$ </p>
<p align="center"> $y = pj * sin(lng)$ </p>
Simplifying these, we get:
<p align="center"> $x = R_{Earth} * sin(lat) * cos(lng)$ </p>
<p align="center"> $y = R_{Earth} * sin(lat) * sin(lng)$ </p>
<p align="center"> $z = R_{Earth} * cos(lat)$ </p>
- Then we can calculate the angle between two points in the 3D space using dot product, which then can be used to calculate the length of the arc between those two points (which is the approximation of the geographical distance).