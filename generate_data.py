import numpy as np
import pandas as pd
import sqlite3

def generate_telecom_node_data(num_records: int = 5000) -> pd.DataFrame:
    """Generates synthetic telecom node telemetry data."""
    np.random.seed(42)
    
    # 1. Core Data Types & Array Operations (NumPy)
    node_ids = [f"gNodeB-{np.random.randint(100, 110)}" for _ in range(num_records)]
    timestamps = pd.date_range(start="2026-01-01", periods=num_records, freq="1min")
    
    # Normal network conditions
    latency_ms = np.random.normal(loc=18.0, scale=3.0, size=num_records)
    packet_loss_pct = np.random.exponential(scale=0.2, size=num_records)
    cpu_utilization = np.random.uniform(low=20.0, high=65.0, size=num_records)
    handover_failures = np.random.poisson(lam=1.2, size=num_records)
    is_anomaly = np.zeros(num_records, dtype=int)

    # 2. Inject Anomalies (e.g., node congestion, pod resource starvation)
    anomaly_indices = np.random.choice(num_records, size=int(num_records * 0.05), replace=False)
    latency_ms[anomaly_indices] += np.random.uniform(50, 120, size=len(anomaly_indices))
    packet_loss_pct[anomaly_indices] += np.random.uniform(5, 15, size=len(anomaly_indices))
    cpu_utilization[anomaly_indices] += np.random.uniform(25, 35, size=len(anomaly_indices))
    handover_failures[anomaly_indices] += np.random.randint(10, 30, size=len(anomaly_indices))
    is_anomaly[anomaly_indices] = 1

    df = pd.DataFrame({
        "timestamp": timestamps,
        "node_id": node_ids,
        "latency_ms": np.clip(latency_ms, a_min=1.0, a_max=None),
        "packet_loss_pct": np.clip(packet_loss_pct, a_min=0.0, a_max=100.0),
        "cpu_utilization": np.clip(cpu_utilization, a_min=0.0, a_max=100.0),
        "handover_failures": handover_failures,
        "is_anomaly": is_anomaly
    })
    return df

# 3. Store in SQL Database
df = generate_telecom_node_data()
conn = sqlite3.connect("telecom_metrics.db")
df.to_sql("node_metrics", conn, if_exists="replace", index=False)
conn.close()
print("Dataset successfully generated and stored in SQLite database.")
