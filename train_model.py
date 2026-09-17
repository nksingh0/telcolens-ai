import sqlite3
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# 1. SQL Querying
conn = sqlite3.connect("telecom_metrics.db")
query = """
    SELECT 
        timestamp,
        node_id,
        latency_ms,
        packet_loss_pct,
        cpu_utilization,
        handover_failures
    FROM node_metrics
    ORDER BY timestamp ASC
"""
raw_df = pd.read_sql_query(query, conn)
conn.close()

# 2. Pandas Feature Engineering
features = ["latency_ms", "packet_loss_pct", "cpu_utilization", "handover_failures"]

# Rolling averages to capture temporal degradation
for col in features:
    raw_df[f"{col}_rolling_5m"] = raw_df.groupby("node_id")[col].transform(lambda x: x.rolling(5, min_periods=1).mean())

engineered_features = features + [f"{col}_rolling_5m" for col in features]

# 3. Scaling & Modeling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(raw_df[engineered_features])

# Isolation Forest for Unsupervised Anomaly Detection
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X_scaled)

# 4. Save Artifacts
joblib.dump(model, "anomaly_detector.pkl")
joblib.dump(scaler, "scaler.pkl")
print("Model training complete. Artifacts saved: anomaly_detector.pkl, scaler.pkl")
