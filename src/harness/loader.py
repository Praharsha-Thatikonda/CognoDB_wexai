import os
import yaml
import pandas as pd
from dotenv import load_dotenv

from src.harness.adapters.cognodb_adapter import CognoDBAdapter
from src.harness.adapters.neo4j_adapter import Neo4jAdapter
from src.harness.adapters.memgraph_adapter import MemgraphAdapter
from src.harness.adapters.falkordb_adapter import FalkorDBAdapter
from src.harness.adapters.arangodb_adapter import ArangoDBAdapter

ADAPTERS = {
    "cognodb": CognoDBAdapter,
    "neo4j": Neo4jAdapter,
    "memgraph": MemgraphAdapter,
    "falkordb": FalkorDBAdapter,
    "arangodb": ArangoDBAdapter
}

def load_data():
    load_dotenv()
    
    with open("config/platforms.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    print("Loading prepared dataset...")
    try:
        nodes_df = pd.read_csv("data/prepared/nodes.csv")
        edges_df = pd.read_csv("data/prepared/edges.csv")
    except FileNotFoundError:
        print("Error: Dataset not found. Run 'make download-data' first.")
        return
        
    platforms = config.get("platforms", {})
    
    for platform_id, p_config in platforms.items():
        print(f"\n--- Loading data into {p_config['name']} ---")
        
        adapter_cls = ADAPTERS.get(platform_id)
        if not adapter_cls:
            print(f"Skipping {platform_id}: No adapter implemented.")
            continue
            
        adapter = adapter_cls(name=p_config['name'], config=p_config, env=os.environ)
        
        try:
            adapter.connect()
            
            print("Clearing database...")
            adapter.clear_database()
            
            print("Loading nodes...")
            node_count, node_time = adapter.load_nodes(nodes_df)
            print(f"Loaded {node_count} nodes in {node_time:.2f}s ({node_count/node_time:.0f} nodes/sec)")
            
            print("Loading edges...")
            edge_count, edge_time = adapter.load_edges(edges_df)
            print(f"Loaded {edge_count} edges in {edge_time:.2f}s ({edge_count/edge_time:.0f} edges/sec)")
            
        except Exception as e:
            print(f"Failed to load data into {platform_id}: {e}")
        finally:
            adapter.disconnect()

if __name__ == "__main__":
    load_data()
