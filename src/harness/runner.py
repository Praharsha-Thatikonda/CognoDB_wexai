import os
import time
import json
import yaml
import random
import concurrent.futures
import pandas as pd
from dotenv import load_dotenv

from src.harness.loader import ADAPTERS
from src.harness.metrics import MetricsCollector

def run_benchmarks():
    load_dotenv()
    
    with open("config/platforms.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    platforms = config.get("platforms", {})
    bench_config = config.get("benchmark", {})
    
    warmup_iters = bench_config.get("warmup_iterations", 10)
    read_iters = bench_config.get("read_iterations", 100)
    concurrency_sweep = bench_config.get("concurrency_sweep", [1, 10, 40])
    
    print("Loading valid node IDs from data/prepared/nodes.csv...")
    try:
        nodes_df = pd.read_csv("data/prepared/nodes.csv")
        valid_node_ids = nodes_df["id"].tolist()
    except FileNotFoundError:
        print("Error: data/prepared/nodes.csv not found. Did you run 'make download-data'?")
        return

    metrics = MetricsCollector()
    os.makedirs("results/raw", exist_ok=True)
    
    for platform_id, p_config in platforms.items():
        print(f"\n======================================")
        print(f"Benchmarking {p_config['name']}")
        print(f"======================================")
        
        adapter_cls = ADAPTERS.get(platform_id)
        if not adapter_cls:
            continue
            
        adapter = adapter_cls(name=p_config['name'], config=p_config, env=os.environ)
        
        try:
            adapter.connect()
            
            # Select random start nodes for traversals from the actual dataset
            start_nodes = [random.choice(valid_node_ids) for _ in range(read_iters)]
            
            print(f"Running 1-hop traversal ({read_iters} iterations)...")
            latencies = []
            for i in range(warmup_iters + read_iters):
                start = time.time()
                adapter.run_1_hop_traversal(start_nodes[i % read_iters])
                if i >= warmup_iters:
                    latencies.append(time.time() - start)
            metrics.add_metric(platform_id, "1_hop", latencies)
            
            print(f"Running 2-hop traversal ({read_iters} iterations)...")
            latencies = []
            for i in range(warmup_iters + read_iters):
                start = time.time()
                adapter.run_2_hop_traversal(start_nodes[i % read_iters])
                if i >= warmup_iters:
                    latencies.append(time.time() - start)
            metrics.add_metric(platform_id, "2_hop", latencies)

            print(f"Running point lookup ({read_iters} iterations)...")
            latencies = []
            for i in range(warmup_iters + read_iters):
                start = time.time()
                adapter.run_point_lookup(start_nodes[i % read_iters])
                if i >= warmup_iters:
                    latencies.append(time.time() - start)
            metrics.add_metric(platform_id, "point_lookup", latencies)

            print(f"Running indexed lookup ({read_iters} iterations)...")
            latencies = []
            ages = [random.randint(18, 65) for _ in range(read_iters)]
            for i in range(warmup_iters + read_iters):
                start = time.time()
                adapter.run_indexed_lookup(ages[i % read_iters])
                if i >= warmup_iters:
                    latencies.append(time.time() - start)
            metrics.add_metric(platform_id, "indexed_lookup", latencies)
            
            print(f"Running aggregation ({read_iters} iterations)...")
            latencies = []
            for i in range(warmup_iters + read_iters):
                start = time.time()
                adapter.run_aggregation()
                if i >= warmup_iters:
                    latencies.append(time.time() - start)
            metrics.add_metric(platform_id, "aggregation", latencies)
            
            print(f"Running mixed workload concurrency sweep...")
            for clients in concurrency_sweep:
                duration = 10 # 10 seconds per concurrency level
                print(f"  -> Concurrency {clients} for {duration}s...")
                
                start_time = time.time()
                ops_completed = 0
                
                def worker():
                    nonlocal ops_completed
                    while time.time() - start_time < duration:
                        adapter.run_mixed_workload_step(valid_node_ids)
                        ops_completed += 1
                        
                with concurrent.futures.ThreadPoolExecutor(max_workers=clients) as executor:
                    futures = [executor.submit(worker) for _ in range(clients)]
                    concurrent.futures.wait(futures)
                    
                throughput = ops_completed / duration
                metrics.add_throughput(platform_id, f"mixed_throughput_c{clients}", throughput)
            
            # Save raw results
            with open(f"results/raw/{platform_id}.json", "w") as f:
                json.dump(metrics.results[platform_id], f, indent=2)
                
        except Exception as e:
            print(f"Benchmark failed for {platform_id}: {e}")
        finally:
            adapter.disconnect()

    print("\nAggregating results...")
    summary = metrics.get_summary()
    df = pd.DataFrame(summary).T
    df.to_csv("results/aggregated.csv", index_label="Platform")
    print("Saved to results/aggregated.csv")

if __name__ == "__main__":
    run_benchmarks()
