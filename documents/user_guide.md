# User Guide: Running the CognoDB Benchmark Suite

This document outlines the end-to-end process for setting up the environment, provisioning the databases, running the benchmarks, and generating the final reports. 

Follow this guide to get the total project working and running.

---

## Step 1: Environment Setup

The benchmarking framework is written in Python. Ensure you have Python 3.11+ installed on your system.

1. **Navigate to the application folder:**
   Open your terminal and navigate to the project directory:
   ```bash
   cd git_application
   ```

2. **Install dependencies:**
   We use a `Makefile` to simplify command execution. Run the setup command to install all required pip packages (like `neo4j`, `pandas`, `matplotlib`, etc.):
   ```bash
   make setup
   ```

---

## Step 2: Database Provisioning & Configuration

To run a fair benchmark, you must provision instances for each of the 5 databases on their respective free tiers. 

1. **Create your `.env` file:**
   We have provided a template called `.env.example`. Copy this to a new file named `.env`.
   *(Note: `.env` is explicitly ignored by Git to prevent your passwords from leaking).*
   ```bash
   cp .env.example .env
   ```

2. **Provision the Databases and Update `.env`:**

   *   **CognoDB Cloud**: Go to the CognoDB console, spin up a free instance, and copy the Bolt URI, username, and password into `COGNODB_URI`, `COGNODB_USER`, and `COGNODB_PASSWORD`.
   *   **Neo4j AuraDB**: Go to Neo4j Aura, create a free instance, and copy the connection details to the `NEO4J_...` variables.
   *   **Memgraph**: If using Docker, run `docker run -p 7687:7687 memgraph/memgraph`. Leave username/password blank in `.env` if local auth is disabled.
   *   **FalkorDB**: If using Docker, run `docker run -p 6379:6379 falkordb/falkordb`.
   *   **ArangoDB Oasis**: Sign up for a free trial on ArangoGraph, create a deployment, and copy the URI and credentials to the `ARANGODB_...` variables.

---

## Step 3: Dataset Preparation

We use the Enron Email dataset (`Email-Enron.txt`) to test the databases on a realistic social network structure containing ~367,000 edges.

1. **Process the dataset:**
   Run the following command. The script will parse the raw `.txt` file, generate synthetic properties (like `age` and `active` status) required for the benchmark queries, and output `nodes.csv` and `edges.csv` into the `data/prepared/` directory.
   ```bash
   make download-data
   ```

---

## Step 4: Execute the Benchmark

With the environment configured and the data prepared, you can now run the suite. 

1. **Load the data into the databases:**
   This step connects to all 5 platforms, clears any existing data, creates the necessary indexes (e.g., on `id` and `age`), and bulk-loads the `nodes.csv` and `edges.csv` files.
   ```bash
   make load-data
   ```

2. **Run the workload metrics:**
   This is the core of the project. The runner will execute 10 warm-up queries (to prime the cache) followed by 100 timed iterations for 1-hop, 2-hop, 3-hop traversals, lookups, and aggregations. It will also run a concurrency sweep (1, 10, 40 clients) to test mixed read/write throughput.
   ```bash
   make benchmark
   ```
   *The raw JSON results for each platform will be saved in `results/raw/`, and the aggregated percentiles will be saved to `results/aggregated.csv`.*

---

## Step 5: Report Generation

Once the benchmark finishes, you need to format the dry numbers into an engaging format for your GitHub repository.

1. **Generate the charts and README:**
   ```bash
   make report
   ```
   This script reads `results/aggregated.csv` and automatically generates:
   *   A Markdown table of all results.
   *   A `latency.png` bar chart showing p50 and p95 latencies.
   *   A `throughput.png` bar chart showing concurrent operations per second.
   *   It then overwrites `README.md` with these elements included.

---

## Step 6: One-Command Execution (Optional)

If you have already configured your `.env` file, you can run Steps 3, 4, and 5 entirely automatically with a single command:

```bash
make all
```

This fulfills the Wexa AI requirement for "Automated, one-command reproducibility".

---

## Final Step: Submission

After running `make all` and ensuring the charts look correct, commit your changes in the `git_application` folder (making sure `.env` is ignored) and push the repository to GitHub. Email the link to `hr@wexa.ai` before your 48-hour deadline expires!
