# PTNet-Analysis
This is my own implementation of the research paper [A comparative study of topological analysis and temporal network analysis of a public transport system](https://www.sciencedirect.com/science/article/pii/S204604302100037X)

Read more about L-space graph: [Statistical analysis of 22 public transport networks in Poland](https://arxiv.org/pdf/physics/0506074)

## Table of Contents
- [0. Overview](#0-overview)
- [1. Technical details](#1-technical-details)
  - [1.1 The method to approximate the geographical distance](#11-the-method-to-approximate-the-geographical-distance)

## 0. Overview:
### Graph stats: 4370 nodes / 5442 edges (vs. paper 4350/5397).
### Build time & memory:
|  Action(s) \ Stats | Time (seconds)  | Mem / Peak mem (MB) |
| :----------------- | :-------------: | :-----------------: |
| **Build**          | 107.308         | 6.97 / 10.49        |
| **Build + Save**   | 154.249         | 0.27 / 11.62        |
| **Load**           | 0.228           | 5.80 / 19.49        |

## 1. Technical details:

### 1.1 The method to approximate the geographical distance:
- The idea is to create a 3D point ($L_{i}$) for each geographical location:
- Assume Earth is a sphere in the 3D space, with the origin O located at the middle of the sphere. The latitude ($lat$) will be the angle between Oz and the secant line ($sc$) of O and $L_{i}$, the longitude ($lng$) will be the angle between Ox and the projection of ($sc$) on Oxy (lets call the length of the projection $pj$).
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