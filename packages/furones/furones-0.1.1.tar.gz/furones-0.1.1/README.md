# Furones: Approximate Independent Set Solver

![In Loving Memory of Asia Furones (The Grandmother I Never Knew)](docs/furones.jpg)

This work builds upon [A Sqrt(n)-Approximation for Independent Sets: The Furones Algorithm](https://dev.to/frank_vega_987689489099bf/the-furones-algorithm-15lp).

---

# Maximum Independent Set (MIS) Problem: Overview

## Definition

The **Maximum Independent Set (MIS)** problem is a fundamental NP-hard problem in graph theory. Given an undirected graph $G = (V, E)$, an _independent set_ is a subset of vertices $S \subseteq V$ where no two vertices in $S$ are adjacent. The MIS problem seeks the largest such subset $S$.

## Key Properties

- **NP-Hardness**: MIS is computationally intractable (no known polynomial-time solution unless $P = NP$).
- **Equivalent Problems**:
  - MIS is equivalent to finding the largest _clique_ in the complement graph $\overline{G}$.
  - It is also related to the _Minimum Vertex Cover_ problem: $S$ is an MIS iff $V \setminus S$ is a vertex cover.

## Applications

1. **Scheduling**: Assigning non-conflicting tasks (e.g., scheduling exams with no shared students).
2. **Network Design**: Selecting non-adjacent nodes for efficient resource allocation.
3. **Bioinformatics**: Modeling protein-protein interaction networks.

## Algorithms

| Approach            | Description                                                            | Complexity          |
| ------------------- | ---------------------------------------------------------------------- | ------------------- |
| Brute-Force         | Checks all possible subsets of vertices.                               | $O(2^n)$            |
| Greedy Heuristics   | Selects vertices with minimal degree iteratively.                      | $O(n + m)$ (approx) |
| Dynamic Programming | Used for trees or graphs with bounded treewidth.                       | $O(3^{tw})$         |
| Approximation       | No PTAS exists; best-known approximation ratio is $O(n / (\log n)^2)$. | NP-Hard             |

## Example

For a graph with vertices $\{A, B, C\}$ and edges $\{(A,B), (B,C)\}$:

- **Independent Sets**: $\{A, C\}$, $\{A\}$, $\{B\}$, $\{C\}$.
- **MIS**: $\{A, C\}$ (size 2).

## Open Challenges

- Finding a constant-factor approximation for general graphs.
- Efficient quantum or parallel algorithms for large-scale graphs.

---

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Answer: Find a Maximum Independent Set.

### Example Instance: 5 x 5 matrix

|        | c1  | c2  | c3  | c4  | c5  |
| ------ | --- | --- | --- | --- | --- |
| **r1** | 0   | 0   | 1   | 0   | 1   |
| **r2** | 0   | 0   | 0   | 1   | 0   |
| **r3** | 1   | 0   | 0   | 0   | 1   |
| **r4** | 0   | 1   | 0   | 0   | 0   |
| **r5** | 1   | 0   | 1   | 0   | 0   |

The input for undirected graph is typically provided in [DIMACS](http://dimacs.rutgers.edu/Challenges) format. In this way, the previous adjacency matrix is represented in a text file using the following string representation:

```
p edge 5 4
e 1 3
e 1 5
e 2 4
e 3 5
```

This represents a 5x5 matrix in DIMACS format such that each edge $(v,w)$ appears exactly once in the input file and is not repeated as $(w,v)$. In this format, every edge appears in the form of

```
e W V
```

where the fields W and V specify the endpoints of the edge while the lower-case character `e` signifies that this is an edge descriptor line.

_Example Solution:_

Independent Set Found `4, 5`: Nodes `4`, and `5` constitute an optimal solution.

---

# Compile and Environment

## Prerequisites

- Python ≥ 3.12

## Installation

```bash
pip install furones
```

## Execution

1. Clone the repository:

   ```bash
   git clone https://github.com/frankvegadelgado/furones.git
   cd furones
   ```

2. Run the script:

   ```bash
   asia -i ./benchmarks/testMatrix1
   ```

   utilizing the `asia` command provided by Furones's Library to execute the Boolean adjacency matrix `furones\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support `.xz`, `.lzma`, `.bz2`, and `.bzip2` compressed text files.

   **Example Output:**

   ```
   testMatrix1: Independent Set Found 4, 5
   ```

   This indicates nodes `4, 5` form a Independent Set.

---

## Independent Set Size

Use the `-c` flag to count the nodes in the Independent Set:

```bash
asia -i ./benchmarks/testMatrix2 -c
```

**Output:**

```
testMatrix2: Independent Set Size 5
```

---

# Command Options

Display help and options:

```bash
asia -h
```

**Output:**

```bash
usage: asia [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Independent Set for undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the Independent Set
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Batch Execution

Batch execution allows you to solve multiple graphs within a directory consecutively.

To view available command-line options for the `batch_asia` command, use the following in your terminal or command prompt:

```bash
batch_asia -h
```

This will display the following help information:

```bash
usage: batch_asia [-h] -i INPUTDIRECTORY [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Independent Set for all undirected graphs encoded in DIMACS format and stored in a directory.

options:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        Input directory path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the Independent Set
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Testing Application

A command-line utility named `test_asia` is provided for evaluating the Algorithm using randomly generated, large sparse matrices. It supports the following options:

```bash
usage: test_asia [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Furones Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a factor of at most 2
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the Independent Set
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Code

- Python implementation by **Frank Vega**.

---

# Complexity

```diff
+ We present a polynomial-time algorithm achieving a Sqrt(n)-approximation ratio for MIS, providing strong evidence that P = NP by efficiently solving a computationally hard problem with near-optimal solutions.
```

---

# License

- MIT License.
