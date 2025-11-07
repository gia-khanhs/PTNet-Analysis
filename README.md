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
- The idea is to create a 3D point for each geographical location (L<sub>i</sub>):
- Assume Earth is a sphere in the 3D space, with the origin O located at the middle of the sphere. The latitude will be the angle between Oz and the secant line (sc) of O and L<sub>i</sub>, the longitude will be the angle between Ox and the projection of (sc) on Oxy (lets call the projection pj).
- Knowing these, we can calculate the 3D position as follow:
Let L<sub>i</sub>(x, y, z).
<p align="center"> z = R<sub>Earth</sub> * cos(lat) <p>
<p align="center"> pj = $\sqrt{R<sub>Earth</sub>² - z²}$ = R<sub>Earth</sub> * sin(lat) <p>
<p align="center"> x = pj * cos(lng) <p>
<p align="center"> y = pj * sin(lng) <p>
