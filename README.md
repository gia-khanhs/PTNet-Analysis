# PTNet-Analysis
This is my own implementation of the research paper "A comparative study of topological analysis and temporal network analysis of a public transport system"!

Link to the paper: https://www.sciencedirect.com/science/article/pii/S204604302100037X

Read more about L-space graph: https://arxiv.org/pdf/physics/0506074

## 0. Some notes on my implementation:

### 0.1 Graph comparision with the paper:
- My implemented graph is a directed single graph. Between stop pairs in walk distance, an edge will be created, and if there is already one (in a bus route), it will be overwritten so that the time weight is minimum.
- My topological graph has 4370 nodes and 5442 edges (without taking edges between stop pair in walk distance into consideration), while the author's has 4350 nodes and 5397.

### 0.2 Resources taken to build the graph:
Time elapsed: 107.308 s
Current memory usage: 6.97 MB; Peak: 10.49 MB

### 0.2 Resources taken to build and save the graph:
Time elapsed: 154.249 s
Current memory usage: 0.27 MB; Peak: 11.62 MB

### 0.3 Resources taken to load the graph:
Time elapsed: 0.228 s
Current memory usage: 5.80 MB; Peak: 19.49 MB

## 1.Technical details:

### 1.1 The method to approximate the geographical distance:
- The idea is to create a 3D point ($L_{i}$) for each geographical location:
- Assume Earth is a sphere in the 3D space, with the origin O located at the middle of the sphere. The latitude will be the angle between Oz and the secant line ($sc$) of O and $L_{i}$, the longitude will be the angle between Ox and the projection of ($sc$) on Oxy (lets call the length of the projection $pj$).
- Knowing these, we can calculate the 3D position as follow:
Let $L_{i}(x, y, z)$
<p align="center"> $z = R_{Earth} * cos(lat)$ </p>
<p align="center"> $pj = \sqrt{R_{Earth}² - z²} = R_{Earth} * sin(lat)$ </p>
<p align="center"> $x = pj * cos(lng)$ </p>
<p align="center"> $y = pj * sin(lng)$ </p>
Simplifying these, we get:
<p align="center"> $x = R_{Earth} * sin(lat) * cos(lng)$ </p>
<p align="center"> $y = R_{Earth} * sin(lat) * sin(lng)$ </p>
<p align="center"> $z = R_{Earth} * cos(lat)$ </p>

- The rest is trivial: Then we can calculate the angle between two points in the 3D space using dot product, which then can be used to calculate the length of the arc between those two points (which is the approximation of the geographical distance).