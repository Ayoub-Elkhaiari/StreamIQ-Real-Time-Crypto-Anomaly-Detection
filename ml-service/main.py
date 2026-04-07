import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = Path("/app/model/anomaly_model.pkl")
META_PATH = Path("/app/model/model_metadata.json")

FEATURES = [
    "current_price",
    "total_volume",
    "price_change_percentage_24h",
    "price_change_percentage_1h",
    "high_low_range_pct",
    "volume_to_market_cap",
    "market_cap_rank",
    "circulating_supply",
    "price_vs_high_24h",
    "price_vs_low_24h",
]

app = FastAPI(title="StreamIQ ML Service")
model: Any = None
metadata: dict[str, Any] = {}


class PredictRequest(BaseModel):
    coin_id: str
    symbol: str
    current_price: float
    total_volume: float
    price_change_percentage_24h: float
    price_change_percentage_1h: float
    high_low_range_pct: float
    volume_to_market_cap: float
    market_cap_rank: float
    circulating_supply: float
    price_vs_high_24h: float
    price_vs_low_24h: float


def severity(score: float) -> str:
    if score < -0.3:
        return "HIGH"
    if score < -0.1:
        return "MEDIUM"
    return "NORMAL"


def load_model() -> bool:
    global model, metadata
    try:
        model = joblib.load(MODEL_PATH)
        metadata = json.loads(META_PATH.read_text(encoding="utf-8")) if META_PATH.exists() else {}
        return True
    except Exception:
        model = None
        metadata = {}
        return False


@app.on_event("startup")
def startup() -> None:
    load_model()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/model-info")
def model_info() -> dict[str, Any]:
    return {
        "version": metadata.get("version", "1.0.0"),
        "features": metadata.get("features", FEATURES),
        "contamination": metadata.get("contamination", 0.03),
        "training_date": metadata.get("training_date"),
    }


@app.post("/reload")
def reload_model() -> dict[str, Any]:
    return {"status": "ok" if load_model() else "failed", "model_loaded": model is not None}


@app.post("/predict")
def predict(payload: PredictRequest) -> dict[str, Any]:
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    df = pd.DataFrame([{k: getattr(payload, k) for k in FEATURES}])
    score = float(model.decision_function(df)[0])
    is_anomaly = int(model.predict(df)[0]) == -1

    return {
        "coin_id": payload.coin_id,
        "symbol": payload.symbol,
        "anomaly_score": round(score, 4),
        "is_anomaly": bool(is_anomaly),
        "severity": severity(score),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
