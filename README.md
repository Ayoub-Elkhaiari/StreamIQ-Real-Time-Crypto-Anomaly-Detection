# StreamIQ — Real-Time Crypto Anomaly Detection

StreamIQ monitors top 50 cryptocurrencies with CoinGecko public data and flags anomalous market conditions in real time.

## No API key required
CoinGecko endpoint is public/free, no signup needed.

## Train first (required)
```bash
docker-compose run --rm ml-service python train.py
```
This generates:
- `ml-service/model/anomaly_model.pkl`
- `ml-service/model/model_metadata.json`

## Run everything
```bash
docker-compose up --build
```
`airflow-init` runs automatically to initialize/migrate Airflow metadata before `airflow-webserver` and `airflow-scheduler` start.

## Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- ML service: http://localhost:8001
- Airflow UI: http://localhost:8088
- Kafka: localhost:9092
- Postgres: localhost:5432
- Redis: localhost:6379

## Data flow
1. `coingecko-producer` polls CoinGecko every 30s and publishes 50 coins to Kafka.
2. `spark-streaming` consumes `crypto_prices`, calls ml-service `/predict`, writes snapshots and anomalies to PostgreSQL, and updates Redis cache.
3. `backend-api` serves dashboard endpoints from Redis (with PostgreSQL fallback).
4. `frontend` polls APIs every 30/60 seconds for live views.

## Airflow daily retraining
- DAG `retrain_model` runs at **02:00 UTC daily**.
- It extracts recent normal data, retrains IsolationForest, validates contamination bounds, deploys model, then reloads ml-service.

## PDF export
Click **📥 Export PDF** in the Recent Anomalies panel.
Output file: `streamiq-crypto-report-YYYY-MM-DD-HH-mm.pdf`.
