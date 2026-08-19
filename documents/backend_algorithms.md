# Graph Database Backend Logic, Algorithms, and Methods
**Research & Implementation Guide for CognoDB Benchmarking**

This document outlines the core backend logic, traversal algorithms, and query optimization methods derived from current graph database research (including LDBC SNB methodologies and ArXiv research) for direct implementation in our benchmarking suite.

---

## 1. Core Traversal Algorithms

Graph benchmarking relies on testing how efficiently the backend engine processes connections. The implementation should stress test the following algorithmic behaviors:

### Breadth-First Search (BFS) / Shortest Path
*   **Logic**: Explores the graph layer by layer. Essential for finding the shortest path between two nodes in an unweighted graph.
*   **Implementation in Benchmark**: 
    *   Our `1-hop`, `2-hop`, and `3-hop` traversals in `src/harness/adapters/` test the database's BFS efficiency.
    *   **Direct Cypher implementation**: `MATCH (n)-[*1..3]->(m) RETURN m`
*   **Research insight**: Index-free adjacency databases execute this in $O(k^d)$ where $k$ is the average degree and $d$ is depth.

### Depth-First Search (DFS) / Path Finding
*   **Logic**: Explores a branch deeply before backtracking. Used for cycle detection or finding any valid path.
*   **Implementation**: Can be tested via complex path queries with filtering.

### Structural Aggregations (Graphalytics)
*   **Logic**: Operations that touch the entire graph, such as PageRank, Community Detection (Louvain), or Connected Components.
*   **Implementation in Benchmark**: 
    *   Our `aggregation` queries evaluate the BI (Business Intelligence) aspect of the graph engine.
    *   **Cypher**: `MATCH (n) RETURN n.age, count(n)` tests global property grouping.

---

## 2. Query Optimization Methods

To ensure accurate and fair benchmarks, the queries we generate must follow industry best practices for optimization, otherwise, we are benchmarking poorly written queries rather than the engine itself.

### Anchor Selection & Indexing
*   **Method**: Always start a traversal from a highly selective "anchor" node.
*   **Direct Implementation**: 
    *   Ensure all database adapters (Neo4j, ArangoDB, etc.) explicitly create an index on the `id` and `age` fields during the `load_data` phase.
    *   **Cypher**: `CREATE INDEX ON :User(id)`

### Path Bounding
*   **Method**: Unbounded traversals (`MATCH (a)-[*]->(b)`) cause exponential memory explosion.
*   **Direct Implementation**: All our traversal benchmarks rigidly bound the hops (`-[:FOLLOWS*2]->`, `-[:FOLLOWS*3]->`) to prevent artificial timeouts.

### Early Filtering
*   **Method**: Apply node property filters before expanding edges to reduce the "fan-out" factor.
*   **Direct Implementation**: Place `WHERE` clauses on the anchor node before the relationship declaration in the query generator.

---

## 3. Workload Design (Inspired by LDBC SNB)

The Linked Data Benchmark Council (LDBC) Social Network Benchmark (SNB) dictates that a robust graph benchmark must simulate real-world behaviors.

### Interactive Workload (OLTP)
*   **Logic**: High concurrency, short response times, localized graph neighborhoods.
*   **Implementation**:
    *   Our `run_mixed_workload_step` function.
    *   Uses a ThreadPoolExecutor to sweep concurrency (1, 10, 40 clients) to test the database's connection pooling and lock contention.
    *   Randomly mixes 90% read queries (local 1-hop traversals) and 10% write queries (inserting new edges).

### Business Intelligence Workload (OLAP)
*   **Logic**: Complex read-only queries that aggregate large portions of the graph.
*   **Implementation**: 
    *   Our `run_aggregation` function tests how well the backend engine handles full table scans and memory management for grouping.

---

## 4. Measuring Accuracy & Precision

To ensure the benchmark yields precise and accurate results:

*   **Warm-up Iterations**: Discard the first 10 runs to negate cold-start latencies and allow the database query planner to cache the execution path.
*   **Percentile Reporting**: Averages (means) are skewed by network spikes. Use NumPy to calculate `p50` (median) and `p95` (tail latency).
*   **Uniform Hardware Constraints**: Run all containerized instances with identical `--cpus` and `--memory` limits to isolate algorithmic efficiency from hardware advantages.
