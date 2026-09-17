from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
from diagnostic_agent import AnomalyDiagnosticAgent

app = FastAPI(title="TelcoLens Anomaly Detection & Diagnostic Service")

# Load artifacts
model = joblib.load("anomaly_detector.pkl")
scaler = joblib.load("scaler.pkl")
agent = AnomalyDiagnosticAgent()

class MetricPayload(BaseModel):
    node_id: str
    latency_ms: float
    packet_loss_pct: float
    cpu_utilization: float
    handover_failures: int

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
def predict_anomaly(data: MetricPayload):
    # Prepare feature vector (including simulated rolling values)
    raw_vals = [data.latency_ms, data.packet_loss_pct, data.cpu_utilization, data.handover_failures]
    feature_vector = np.array(raw_vals + raw_vals).reshape(1, -1)
    
    scaled_vector = scaler.transform(feature_vector)
    prediction = model.predict(scaled_vector)  # -1 is anomaly, 1 is normal
    
    is_anomaly = bool(prediction[0] == -1)
    response = {
        "node_id": data.node_id,
        "is_anomaly": is_anomaly,
        "diagnosis": None
    }
    
    # If anomaly detected, invoke the GenAI / Diagnostic Agent
    if is_anomaly:
        mock_log = f"gNodeB[{data.node_id}] WARNING: Keepalive timeout. SCTP link retransmitting."
        response["diagnosis"] = agent.run_root_cause_analysis(
            node_id=data.node_id,
            telemetry=data.model_dump(),
            mock_k8s_log=mock_log
        )
        
    return response
