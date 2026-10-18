# Progress Summary 1

## Pseudocode

## Data Sources

| Data Source | Description | Provenance |
| --- | --- | --- |
| Launch Library 2 | Free, returns a lot of data | Part of TheSpaceDevs, same organization as Space Launch Now, not an independent source |
| NASA | Free, returns a lot of data | NASA |
| CelesTrak | Free, no key, TLE data source | Republishes the same Space-Track/USSF catalogue, easier to use than Space-Track directly |
| Space-Track | Free, TLE data source | U.S. Space Force |
| FAA | Per-launch license data | U.S. Federal Aviation Administration |
| RocketLaunch.live | Free tier limited to next 5 launches, full access needs a key | Independent operator, data lineage unconfirmed |
| KeepTrack | Free with key, TLE and launch data | Combines data from multiple sources, including Space-Track and CelesTrak |
| SatNOGS | Free, radio-frequency satellite observation data | Amateur ground station network receiving actual satellite signals, independent of the Space-Track catalogue lineage |
| ESA DISCOS | Free, TLE and launch data, normally only available to research and state institutions | European Space Agency, an independent catalogue from Space-Track |


https://www.faa.gov/data_research/commercial_space_data

https://www.rocketlaunch.live/

https://nextspaceflight.com/api_access/

https://github.com/shahar603/Launch-Dashboard-API/wiki

https://keeptrack.space/api

https://hackaday.io/project/1340/logs?sort=newest&page=2


## Literature Review of Applicable Accademic Research

This paper studies the impact of false data injection attacks on state estimation in electric power grids. Most of the discussion is focused on the power grid, but the concepts are applicable. The authors take a novel approach in applying an ellipsoidal algorithm to computer upper and lower bounds of such data sets, thereby making it more difficult for an attacker to inject false data into the system. 

**Elipsoid Algorithm** is a mathematical method that uses ellipsoids to approximate the feasible range of a set of points.

https://math.mit.edu/~goemans/18453S17/ellipsoid-notes.pdf

Yao Liu, Peng Ning, and Michael K. Reiter. 2011. False data injection attacks against state estimation in electric power grids. ACM Trans. Inf. Syst. Secur. 14, 1, Article 13 (May 2011), 33 pages. https://doi.org/10.1145/1952982.1952995


### Integrating conflicting data: the role of source dependence

In this paper, the authors discuss problems very similar to the ones we are trying to overcome. They discuss the problem of integrating data from multiple sources, without knowing of the reliability or independence of each source. Their novel approach aims to consider dependence between sources and by applying Bayesian analysis, they are able to determine the analysis functions using real world and simulated data.

**Bayesian analysis** is a statistcal method that uses Bayes theorem to update the probability for a hypothesis as more evidence or information becomes available. The authors use this method to determine reliability of each source.

**Bayes Theorem** is a mathematical formula that describes how to update the probabilities of hypothesis when given evidence.

https://bayesian.org/what-is-bayesian-analysis/

Xin Luna Dong, Laure Berti-Equille, and Divesh Srivastava. 2009. Integrating conflicting data: the role of source dependence. Proc. VLDB Endow. 2, 1 (August 2009), 550–561. https://doi.org/10.14778/1687627.1687690