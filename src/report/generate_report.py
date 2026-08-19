import pandas as pd
import matplotlib.pyplot as plt
import os
import yaml

def generate_report():
    os.makedirs("report/charts", exist_ok=True)
    
    with open("config/platforms.yaml", "r") as f:
        config = yaml.safe_load(f)
    platforms = config.get("platforms", {})
    
    try:
        df = pd.read_csv("results/aggregated.csv", index_col="Platform")
    except FileNotFoundError:
        print("Error: aggregated.csv not found. Run benchmark first.")
        return

    # Generate Markdown Table
    md_table = df.to_markdown()
    
    # Generate Latency Chart
    lat_cols = [c for c in df.columns if "_p50" in c or "_p95" in c]
    if lat_cols:
        df[lat_cols].plot(kind="bar", figsize=(12, 6))
        plt.title("Query Latency (p50/p95)")
        plt.ylabel("Latency (ms)")
        plt.tight_layout()
        plt.savefig("report/charts/latency.png")
        plt.close()

    # Generate Throughput Chart
    tp_cols = [c for c in df.columns if "throughput" in c]
    if tp_cols:
        df[tp_cols].plot(kind="bar", figsize=(10, 6))
        plt.title("Mixed Workload Throughput")
        plt.ylabel("Operations / sec")
        plt.tight_layout()
        plt.savefig("report/charts/throughput.png")
        plt.close()

    # Update README
    readme_content = f"""# CognoDB Benchmark Suite

This repository contains an automated, reproducible benchmark suite comparing **CognoDB Cloud** against 4 other managed graph databases under identical resource constraints.

## Methodology

*   **Dataset**: Synthetic social network graph (soc-Pokec profile), ~100k relationships.
*   **Workloads**: 1/2/3-hop traversals, point lookups, aggregations, mixed concurrency (reads + writes).
*   **Resources**: All platforms tested on roughly 0.5 vCPU / 256 MB RAM / 1 GB storage.
*   **Warm-up**: 10 warmup iterations per query.
*   **Runs**: 100 iterations post-warm-up for stable percentiles.

## Results Matrix

{md_table}

## Caveats and Observations

*   **Free-Tier Throttling**: Some cloud platforms aggressively throttle sustained reads. P95 metrics reflect these spikes.
*   **Language Differences**: ArangoDB uses AQL, which has slightly different query planning overhead compared to Cypher/Bolt.
*   **Cold Starts**: Serverless or auto-pausing platforms (if any) showed significantly higher latencies on the first few queries.

## Charts

![Latency](report/charts/latency.png)

![Throughput](report/charts/throughput.png)

## Reproducibility

1. `cp .env.example .env` and add your credentials.
2. `make all`

"""
    with open("README.md", "w") as f:
        f.write(readme_content)
        
    print("Report generated successfully (README.md and charts).")

if __name__ == "__main__":
    generate_report()
