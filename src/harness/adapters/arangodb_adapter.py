import time
import pandas as pd
from typing import Dict, Any, Tuple
from arango import ArangoClient
from src.harness.base_adapter import BaseAdapter
import random

class ArangoDBAdapter(BaseAdapter):
    def __init__(self, name: str, config: Dict[str, Any], env: Dict[str, str]):
        super().__init__(name, config, env)
        self.client = None
        self.db = None
        self.uri = env.get(f"{self.prefix}_URI")
        self.user = env.get(f"{self.prefix}_USER")
        self.password = env.get(f"{self.prefix}_PASSWORD")
        self.dbname = env.get(f"{self.prefix}_DBNAME", "_system")

    def connect(self):
        if not self.uri or not self.user or not self.password:
            raise ValueError(f"Missing credentials for {self.name} ({self.prefix})")
        self.client = ArangoClient(hosts=self.uri)
        self.db = self.client.db(self.dbname, username=self.user, password=self.password)

    def disconnect(self):
        if self.client:
            self.client.close()

    def clear_database(self):
        if self.db.has_collection("users"):
            self.db.collection("users").truncate()
        else:
            self.db.create_collection("users")
            
        if self.db.has_collection("follows"):
            self.db.collection("follows").truncate()
        else:
            self.db.create_collection("follows", edge=True)

    def load_nodes(self, df: pd.DataFrame) -> Tuple[int, float]:
        start = time.time()
        
        users_col = self.db.collection("users")
        # Ensure indexes
        users_col.add_hash_index(fields=["id"], unique=True)
        users_col.add_hash_index(fields=["age"])

        records = df.to_dict("records")
        # ArangoDB needs _key to be string if we want to use it, but we'll just store 'id' as a property
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            # Convert 'id' to '_key' string for easier edge linking later
            for r in batch:
                r["_key"] = str(r["id"])
            users_col.import_bulk(batch, on_duplicate="replace")
                
        return len(records), time.time() - start

    def load_edges(self, df: pd.DataFrame) -> Tuple[int, float]:
        start = time.time()
        
        follows_col = self.db.collection("follows")
        records = df.to_dict("records")
        
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            formatted_batch = []
            for r in batch:
                formatted_batch.append({
                    "_from": f"users/{r['source']}",
                    "_to": f"users/{r['target']}"
                })
            follows_col.import_bulk(formatted_batch)
                
        return len(records), time.time() - start

    def run_1_hop_traversal(self, start_node_id: int) -> int:
        query = """
        FOR v IN 1..1 OUTBOUND CONCAT('users/', @id) follows
        COLLECT WITH COUNT INTO length
        RETURN length
        """
        cursor = self.db.aql.execute(query, bind_vars={"id": str(start_node_id)})
        return list(cursor)[0]

    def run_2_hop_traversal(self, start_node_id: int) -> int:
        query = """
        FOR v IN 2..2 OUTBOUND CONCAT('users/', @id) follows
        COLLECT WITH COUNT INTO length
        RETURN length
        """
        cursor = self.db.aql.execute(query, bind_vars={"id": str(start_node_id)})
        return list(cursor)[0]

    def run_3_hop_traversal(self, start_node_id: int) -> int:
        query = """
        FOR v IN 3..3 OUTBOUND CONCAT('users/', @id) follows
        COLLECT WITH COUNT INTO length
        RETURN length
        """
        cursor = self.db.aql.execute(query, bind_vars={"id": str(start_node_id)})
        return list(cursor)[0]

    def run_point_lookup(self, node_id: int) -> Dict:
        query = "FOR u IN users FILTER u.id == @id RETURN u"
        cursor = self.db.aql.execute(query, bind_vars={"id": node_id})
        res = list(cursor)
        return res[0] if res else {}

    def run_indexed_lookup(self, age: int) -> int:
        query = "FOR u IN users FILTER u.age == @age COLLECT WITH COUNT INTO length RETURN length"
        cursor = self.db.aql.execute(query, bind_vars={"age": age})
        return list(cursor)[0]

    def run_aggregation(self) -> int:
        query = "FOR u IN users COLLECT age = u.age WITH COUNT INTO count RETURN {age: age, count: count}"
        cursor = self.db.aql.execute(query)
        return len(list(cursor))

    def run_mixed_workload_step(self, valid_node_ids: list) -> None:
        is_write = random.random() < 0.1
        if is_write:
            id1 = random.choice(valid_node_ids)
            id2 = random.choice(valid_node_ids)
            query = "INSERT { _from: CONCAT('users/', @id1), _to: CONCAT('users/', @id2) } INTO follows"
            self.db.aql.execute(query, bind_vars={"id1": str(id1), "id2": str(id2)})
        else:
            query = "FOR u IN users LIMIT 1 FOR v IN 1..1 OUTBOUND u follows COLLECT WITH COUNT INTO length RETURN length"
            self.db.aql.execute(query)
