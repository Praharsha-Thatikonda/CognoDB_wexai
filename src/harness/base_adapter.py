from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any, Tuple

class BaseAdapter(ABC):
    def __init__(self, name: str, config: Dict[str, Any], env: Dict[str, str]):
        self.name = name
        self.config = config
        self.env = env
        self.prefix = config.get("env_prefix", "")

    @abstractmethod
    def connect(self):
        """Establish connection to the database"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to the database"""
        pass

    @abstractmethod
    def clear_database(self):
        """Wipe all data from the database"""
        pass

    @abstractmethod
    def load_nodes(self, df: pd.DataFrame) -> Tuple[int, float]:
        """Load nodes from DataFrame. Returns (count, time_taken_seconds)"""
        pass

    @abstractmethod
    def load_edges(self, df: pd.DataFrame) -> Tuple[int, float]:
        """Load edges from DataFrame. Returns (count, time_taken_seconds)"""
        pass

    @abstractmethod
    def run_1_hop_traversal(self, start_node_id: int) -> int:
        """Run a 1-hop traversal. Returns count of found paths/nodes"""
        pass

    @abstractmethod
    def run_2_hop_traversal(self, start_node_id: int) -> int:
        """Run a 2-hop traversal. Returns count of found paths/nodes"""
        pass

    @abstractmethod
    def run_3_hop_traversal(self, start_node_id: int) -> int:
        """Run a 3-hop traversal. Returns count of found paths/nodes"""
        pass

    @abstractmethod
    def run_point_lookup(self, node_id: int) -> Dict:
        """Fetch a single node by ID"""
        pass

    @abstractmethod
    def run_indexed_lookup(self, age: int) -> int:
        """Fetch nodes matching an indexed property (e.g. age). Returns count"""
        pass

    @abstractmethod
    def run_aggregation(self) -> int:
        """Run an aggregation query (e.g. count of nodes by age). Returns number of groups"""
        pass

    @abstractmethod
    def run_mixed_workload_step(self, valid_node_ids: list) -> None:
        """Execute one unit of work for the mixed read/write concurrency test"""
        pass
