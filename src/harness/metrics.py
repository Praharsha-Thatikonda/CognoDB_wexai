import numpy as np
from typing import List, Dict

class MetricsCollector:
    def __init__(self):
        self.results = {}
        
    def add_metric(self, platform: str, metric_name: str, values: List[float]):
        if platform not in self.results:
            self.results[platform] = {}
            
        p50 = np.percentile(values, 50) * 1000  # Convert to ms
        p95 = np.percentile(values, 95) * 1000
        mean = np.mean(values) * 1000
        
        self.results[platform][metric_name] = {
            "p50_ms": p50,
            "p95_ms": p95,
            "mean_ms": mean,
            "raw_values_s": values
        }
        
    def add_throughput(self, platform: str, metric_name: str, throughput: float):
         if platform not in self.results:
            self.results[platform] = {}
         self.results[platform][metric_name] = {
             "throughput_ops_sec": throughput
         }

    def get_summary(self) -> Dict:
        # Returns a structure easily serialized to JSON/CSV
        summary = {}
        for platform, metrics in self.results.items():
            summary[platform] = {}
            for metric, data in metrics.items():
                if "p50_ms" in data:
                    summary[platform][f"{metric}_p50"] = data["p50_ms"]
                    summary[platform][f"{metric}_p95"] = data["p95_ms"]
                elif "throughput_ops_sec" in data:
                    summary[platform][metric] = data["throughput_ops_sec"]
        return summary
