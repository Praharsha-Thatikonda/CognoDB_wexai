import os
import random
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
PREPARED_DIR = DATA_DIR / "prepared"

# We will use the Enron email dataset as it fits the 100k-500k requirement well
DATASET_PATH = Path("../datasets/Email-Enron.txt")

def process_dataset(filepath: Path):
    print(f"Processing dataset from {filepath}...")
    
    edges = []
    nodes = set()
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                source = int(parts[0])
                target = int(parts[1])
                edges.append((source, target))
                nodes.add(source)
                nodes.add(target)
                
    print(f"Parsed {len(nodes)} nodes and {len(edges)} edges.")
    
    # Generate synthetic properties for nodes to satisfy the benchmark queries (age, active)
    nodes_df = pd.DataFrame([
        {
            "id": n, 
            "age": random.randint(18, 65), 
            "active": random.choice([True, False])
        } for n in nodes
    ])
    
    edges_df = pd.DataFrame(edges, columns=["source", "target"])
    
    return nodes_df, edges_df

def generate_synthetic_social_graph(num_edges=100000):
    print(f"Generating synthetic social graph with {num_edges} edges...")
    nodes = set()
    edges = []
    
    # Simple preferential attachment / power-law mock
    num_nodes = num_edges // 15
    
    for _ in range(num_edges):
        source = random.randint(1, num_nodes)
        target = random.randint(1, num_nodes)
        while source == target:
            target = random.randint(1, num_nodes)
        
        edges.append((source, target))
        nodes.add(source)
        nodes.add(target)
        
    print(f"Generated {len(nodes)} nodes and {len(edges)} edges.")
    
    nodes_df = pd.DataFrame([{"id": n, "age": random.randint(18, 65), "active": random.choice([True, False])} for n in nodes])
    edges_df = pd.DataFrame(edges, columns=["source", "target"])
    
    return nodes_df, edges_df

def main():
    os.makedirs(PREPARED_DIR, exist_ok=True)
    
    nodes_file = PREPARED_DIR / "nodes.csv"
    edges_file = PREPARED_DIR / "edges.csv"
    
    if nodes_file.exists() and edges_file.exists():
        print("Data already exists. Skipping generation.")
        return

    if not DATASET_PATH.exists():
        # Fallback to Cit-HepPh.txt if Enron is missing, or synthetic if both are missing
        alt_path = Path("../datasets/Cit-HepPh.txt")
        if alt_path.exists():
            print("Enron dataset not found. Falling back to Cit-HepPh.txt")
            nodes_df, edges_df = process_dataset(alt_path)
        else:
            print(f"External datasets not found. Generating a self-contained synthetic dataset.")
            nodes_df, edges_df = generate_synthetic_social_graph()
    else:
        nodes_df, edges_df = process_dataset(DATASET_PATH)
    
    print("Saving to CSV...")
    nodes_df.to_csv(nodes_file, index=False)
    edges_df.to_csv(edges_file, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
