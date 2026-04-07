import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

np.random.seed(42)
N = 50_000


def main() -> None:
    df = pd.DataFrame(
        {
            "current_price": np.abs(np.random.lognormal(5, 3, N)),
            "total_volume": np.abs(np.random.lognormal(18, 3, N)),
            "price_change_percentage_24h": np.random.normal(0, 3, N),
            "price_change_percentage_1h": np.random.normal(0, 1, N),
            "high_low_range_pct": np.abs(np.random.normal(4, 2, N)).clip(0.1, 30),
            "volume_to_market_cap": np.abs(np.random.normal(0.05, 0.03, N)).clip(0.001, 0.5),
            "market_cap_rank": np.random.randint(1, 251, N).astype(float),
            "circulating_supply": np.abs(np.random.lognormal(18, 4, N)),
            "price_vs_high_24h": np.random.normal(-2, 1.5, N).clip(-20, 0),
            "price_vs_low_24h": np.random.normal(2, 1.5, N).clip(0, 20),
        }
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                IsolationForest(
                    n_estimators=200,
                    contamination=0.03,
                    max_samples="auto",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    pipeline.fit(df)

    output_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(pipeline, os.path.join(output_dir, "anomaly_model.pkl"))

    with open(os.path.join(output_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": "1.0.0",
                "model_type": "IsolationForest",
                "features": list(df.columns),
                "contamination": 0.03,
                "training_samples": N,
                "training_date": datetime.utcnow().isoformat(),
                "note": "Bootstrap model — auto-retrained daily with real CoinGecko data via Airflow",
            },
            f,
            indent=2,
        )

    print("Model trained and saved successfully.")
    print(f"Features: {list(df.columns)}")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    main()
