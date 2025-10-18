from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class BenchmarkMetrics:
    near_miss_rate: float
    incident_rate: float
    severe_share: float


def load_oil_gas_benchmark(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def compute_org_metrics(df: pd.DataFrame) -> BenchmarkMetrics:
    hours = max(df.get("hours_worked", pd.Series([200000])).sum(), 1)
    near_misses = int(df.get("near_miss", pd.Series([0])).sum())
    incidents = int(df.get("recordable_incident", pd.Series([0])).sum())
    severe = int(df.get("severe", pd.Series([0])).sum())
    total = max(int(df.get("total_events", pd.Series([near_misses + incidents])).sum()), 1)
    return BenchmarkMetrics(
        near_miss_rate=near_misses * 200000.0 / hours,
        incident_rate=incidents * 200000.0 / hours,
        severe_share=severe / total,
    )


def compare_to_benchmark(org: BenchmarkMetrics, ref: BenchmarkMetrics) -> List[Dict[str, object]]:
    return [
        {
            "metric": "Near-miss rate",
            "unit": "per 200k hrs",
            "organization_value": org.near_miss_rate,
            "benchmark_value": ref.near_miss_rate,
            "delta": org.near_miss_rate - ref.near_miss_rate,
            "interpretation": "Higher can be positive (better reporting culture) if incident rate is low",
        },
        {
            "metric": "Incident rate",
            "unit": "per 200k hrs",
            "organization_value": org.incident_rate,
            "benchmark_value": ref.incident_rate,
            "delta": org.incident_rate - ref.incident_rate,
            "interpretation": "Lower is better; monitor trends",
        },
        {
            "metric": "Severe share",
            "unit": "fraction",
            "organization_value": org.severe_share,
            "benchmark_value": ref.severe_share,
            "delta": org.severe_share - ref.severe_share,
            "interpretation": "Lower is better; investigate high severity concentration",
        },
    ]
