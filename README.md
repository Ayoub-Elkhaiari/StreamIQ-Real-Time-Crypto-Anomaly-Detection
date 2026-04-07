# 🚀 StreamIQ — Real-Time Crypto Anomaly Detection

StreamIQ is a real-time data platform that monitors the **top 50 cryptocurrencies** and detects unusual market behavior using streaming pipelines and machine learning.

Instead of just tracking prices, StreamIQ focuses on **identifying anomalies as they happen** — such as sudden spikes, drops, or abnormal trading activity.

---

## ✨ Why this project?

This project demonstrates how to build a **production-like data system**, combining:

- ⚡ Real-time streaming (Kafka + Spark)
- 🧠 Machine Learning (Isolation Forest)
- 📊 Interactive dashboard (React)
- 🔄 Automated retraining (Airflow)
- 🐳 Fully containerized architecture (Docker)

---

## 🖥️ Dashboard

Here’s a snapshot of the StreamIQ dashboard:

![StreamIQ_](https://github.com/user-attachments/assets/1500f357-ecef-49d3-9cfe-912809d7a8c8)

The dashboard provides:

📈 Live anomaly trends over time
🚨 Real-time anomaly detection table
💰 Volume distribution of top cryptocurrencies
📡 Live system status indicator
📄 One-click PDF report export


## ⚙️ How it works
#### Data Pipeline
1. coingecko-producer fetches market data every 30 seconds
2. Data is streamed into Kafka (crypto_prices topic)
3. spark-streaming processes the stream and calls the ML service
4. Predictions are stored in PostgreSQL and cached in Redis
5. backend-api exposes fast API endpoints
6. frontend updates the dashboard in near real-time

This is a general overview of the system: 
<img width="1536" height="1024" alt="StreamIQ crypto anomaly detection workflow" src="https://github.com/user-attachments/assets/6821c101-e9e5-4e16-95ae-522fff7fb4c1" />


## 🧠 Machine Learning
- Model: Isolation Forest
- Type: Unsupervised anomaly detection
- Uses features like:
- Price changes (1h / 24h)
- Volume ratios
- Market cap rank
- Volatility indicators
- Automatically retrained daily using fresh data

## 🔄 Automation (Airflow)
- Daily retraining at 02:00 UTC
- Pipeline:
   - Extract recent normal data
   - Retrain model
   - Validate contamination rate
   - Deploy new model
   - Reload ML service

## 🚀 Getting Started
1. Train the model (required)
```
docker-compose run --rm ml-service python train.py
```

This generates:

`ml-service/model/anomaly_model.pkl`
`ml-service/model/model_metadata.json`

2. Run the full system
```
docker-compose up --build
```

Airflow initializes automatically before starting its services.

## 🌐 Services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- ML service: http://localhost:8001
- Airflow UI: http://localhost:8088
- Kafka: localhost:9092
- Postgres: localhost:5432
- Redis: localhost:6379

## 📊 Key Features
- ⚡ Real-time anomaly detection (30s latency)
- 📡 Live dashboard updates
- 🧠 ML-powered insights
- 🔁 Automated retraining pipeline
- 📄 Exportable anomaly reports (PDF)
- 🐳 One-command deployment with Docker

This project showcases:

- ✅ End-to-end data engineering pipeline
- ✅ Real-time stream processing
- ✅ ML model deployment in production
- ✅ Microservices architecture
- ✅ Scalable system design


## 👤 Author

Ayoub El Khaiari
MSc in Advanced Machine Learning & Multimedia intelligence
