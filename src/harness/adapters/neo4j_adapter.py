import time
import pandas as pd
from typing import Dict, Any, Tuple
from neo4j import GraphDatabase
from src.harness.base_adapter import BaseAdapter
import random

class Neo4jAdapter(BaseAdapter):
    def __init__(self, name: str, config: Dict[str, Any], env: Dict[str, str]):
        super().__init__(name, config, env)
        self.driver = None
        self.uri = env.get(f"{self.prefix}_URI")
        self.user = env.get(f"{self.prefix}_USER")
        self.password = env.get(f"{self.prefix}_PASSWORD")

    def connect(self):
        if not self.uri:
            raise ValueError(f"Missing URI for {self.name} ({self.prefix})")
        
        if self.user and self.password:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        else:
            self.driver = GraphDatabase.driver(self.uri, auth=None)
            
        self.driver.verify_connectivity()

    def disconnect(self):
        if self.driver:
            self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def load_nodes(self, df: pd.DataFrame) -> Tuple[int, float]:
        start = time.time()
        records = df.to_dict("records")
        
        with self.driver.session() as session:
            # Create index for fast lookups
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:User) ON (n.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:User) ON (n.age)")
            
            query = """
            UNWIND $batch AS row
            MERGE (n:User {id: row.id})
            SET n.age = row.age, n.active = row.active
            """
            
            # Batch loading
            batch_size = 5000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                session.run(query, batch=batch)
                
        return len(records), time.time() - start

    def load_edges(self, df: pd.DataFrame) -> Tuple[int, float]:
        start = time.time()
        records = df.to_dict("records")
        
        with self.driver.session() as session:
            query = """
            UNWIND $batch AS row
            MATCH (s:User {id: row.source})
            MATCH (t:User {id: row.target})
            MERGE (s)-[:FOLLOWS]->(t)
            """
            batch_size = 5000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                session.run(query, batch=batch)
                
        return len(records), time.time() - start

    def run_1_hop_traversal(self, start_node_id: int) -> int:
        query = "MATCH (n:User {id: $id})-[:FOLLOWS]->(m) RETURN count(m) as c"
        with self.driver.session() as session:
            res = session.run(query, id=start_node_id).single()
            return res["c"] if res else 0

    def run_2_hop_traversal(self, start_node_id: int) -> int:
        query = "MATCH (n:User {id: $id})-[:FOLLOWS*2]->(m) RETURN count(m) as c"
        with self.driver.session() as session:
            res = session.run(query, id=start_node_id).single()
            return res["c"] if res else 0

    def run_3_hop_traversal(self, start_node_id: int) -> int:
        query = "MATCH (n:User {id: $id})-[:FOLLOWS*3]->(m) RETURN count(m) as c"
        with self.driver.session() as session:
            res = session.run(query, id=start_node_id).single()
            return res["c"] if res else 0

    def run_point_lookup(self, node_id: int) -> Dict:
        query = "MATCH (n:User {id: $id}) RETURN n"
        with self.driver.session() as session:
            res = session.run(query, id=node_id).single()
            return dict(res["n"]) if res else {}

    def run_indexed_lookup(self, age: int) -> int:
        query = "MATCH (n:User {age: $age}) RETURN count(n) as c"
        with self.driver.session() as session:
            res = session.run(query, age=age).single()
            return res["c"] if res else 0

    def run_aggregation(self) -> int:
        query = "MATCH (n:User) RETURN n.age, count(n) as c"
        with self.driver.session() as session:
            res = list(session.run(query))
            return len(res)

    def run_mixed_workload_step(self, valid_node_ids: list) -> None:
        # A mix of reads and a small write
        is_write = random.random() < 0.1
        with self.driver.session() as session:
            if is_write:
                id1 = random.choice(valid_node_ids)
                id2 = random.choice(valid_node_ids)
                session.run("MATCH (a:User {id: $id1}), (b:User {id: $id2}) MERGE (a)-[:INTERACTS_WITH]->(b)", id1=id1, id2=id2)
            else:
                session.run("MATCH (n:User) WITH n LIMIT 1 MATCH (n)-[:FOLLOWS]->(m) RETURN count(m)")
