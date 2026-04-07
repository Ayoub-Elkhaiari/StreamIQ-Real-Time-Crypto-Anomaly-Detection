import json
import os
from datetime import datetime

import psycopg2
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamiq")
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamiq")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamiq123")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

app = FastAPI(title="StreamIQ Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def pg_conn():
    return psycopg2.connect(host=POSTGRES_HOST, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD)


def redis_conn():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    total_snapshots = total_anomalies = 0
    last_updated = None
    coins_tracked = 50
    try:
        r = redis_conn()
        total_snapshots = int(r.get("stats:total_snapshots") or 0)
        total_anomalies = int(r.get("stats:total_anomalies") or 0)
        last_updated = r.get("stats:last_updated")
    except Exception:
        with pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END),0), COALESCE(MAX(processed_at), NOW()) FROM coin_snapshots")
                total_snapshots, total_anomalies, last_updated = cur.fetchone()
                cur.execute("SELECT COUNT(DISTINCT coin_id) FROM coin_snapshots")
                coins_tracked = int(cur.fetchone()[0] or 0)

    rate = (total_anomalies / total_snapshots * 100) if total_snapshots else 0
    return {
        "total_snapshots": total_snapshots,
        "total_anomalies": total_anomalies,
        "anomaly_rate_pct": round(rate, 2),
        "coins_tracked": coins_tracked,
        "last_updated": str(last_updated or datetime.utcnow().isoformat() + "Z"),
    }


@app.get("/recent-coins")
def recent_coins(limit: int = 50):
    try:
        r = redis_conn()
        rows = r.lrange("stats:recent_coins", 0, max(limit - 1, 0))
        return [json.loads(x) for x in rows]
    except Exception:
        with pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT coin_id,symbol,name,current_price,market_cap_rank,total_volume,price_change_percentage_24h,anomaly_score,is_anomaly,severity,processed_at FROM coin_snapshots ORDER BY processed_at DESC LIMIT %s", (limit,))
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in cur.fetchall()]


@app.get("/recent-anomalies")
def recent_anomalies(limit: int = 20):
    try:
        r = redis_conn()
        rows = r.lrange("stats:recent_anomalies", 0, max(limit - 1, 0))
        return [json.loads(x) for x in rows]
    except Exception:
        with pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT coin_id,symbol,name,current_price,anomaly_score,severity,price_change_percentage_24h,detected_at FROM anomalies ORDER BY detected_at DESC LIMIT %s", (limit,))
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in cur.fetchall()]


@app.get("/anomalies-over-time")
def anomalies_over_time(hours: int = 6):
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT to_char(date_trunc('hour', detected_at) +
                               (floor(date_part('minute', detected_at)/30)*interval '30 min'),'HH24:MI') as bucket,
                       COUNT(*)
                FROM anomalies
                WHERE detected_at >= NOW() - (%s || ' hours')::interval
                GROUP BY 1
                ORDER BY 1
                """,
                (hours,),
            )
            return [{"time_bucket": r[0], "anomaly_count": int(r[1])} for r in cur.fetchall()]


@app.get("/top-anomalies")
def top_anomalies():
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT coin_id,symbol,name,current_price,anomaly_score,severity,detected_at
                FROM anomalies
                ORDER BY anomaly_score ASC
                LIMIT 10
                """
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]


@app.get("/coin-history")
def coin_history(coin_id: str, hours: int = 24):
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT processed_at,current_price,anomaly_score,is_anomaly
                FROM coin_snapshots
                WHERE coin_id=%s AND processed_at >= NOW() - (%s || ' hours')::interval
                ORDER BY processed_at ASC
                """,
                (coin_id, hours),
            )
            return [
                {
                    "processed_at": r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0]),
                    "current_price": float(r[1]),
                    "anomaly_score": float(r[2] or 0),
                    "is_anomaly": bool(r[3]),
                }
                for r in cur.fetchall()
            ]
