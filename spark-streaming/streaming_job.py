import json
import os
import time
from datetime import datetime

import psycopg2
import redis
import requests
from kafka.admin import KafkaAdminClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-broker:9092")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml-service:8001")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "streamiq")
POSTGRES_USER = os.getenv("POSTGRES_USER", "streamiq")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "streamiq123")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
TOPIC = "crypto_prices"


def wait_for_services() -> None:
    for attempt in range(1, 31):
        try:
            admin = KafkaAdminClient(bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS])
            admin.close()
            break
        except Exception:
            print(f"Waiting for Kafka ({attempt}/30)")
            time.sleep(3)
    else:
        raise RuntimeError("Kafka not ready")

    for attempt in range(1, 31):
        try:
            requests.get(f"{ML_SERVICE_URL}/health", timeout=3).raise_for_status()
            return
        except Exception:
            print(f"Waiting for ML service ({attempt}/30)")
            time.sleep(3)
    raise RuntimeError("ML service not ready")


def process_batch(df, epoch_id: int) -> None:
    if df.rdd.isEmpty():
        print(f"epoch {epoch_id}: empty")
        return

    rows = [r.asDict() for r in df.collect()]
    results = []
    for row in rows:
        try:
            response = requests.post(f"{ML_SERVICE_URL}/predict", json=row, timeout=10)
            response.raise_for_status()
            pred = response.json()
            results.append({**row, **pred, "processed_at": datetime.utcnow().isoformat()})
        except Exception as exc:
            print(f"ML service error for {row.get('coin_id')}: {exc}")
            results.append({**row, "anomaly_score": 0.0, "is_anomaly": False, "severity": "NORMAL", "processed_at": datetime.utcnow().isoformat()})

    try:
        conn = psycopg2.connect(host=POSTGRES_HOST, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD)
        cur = conn.cursor()
    except Exception as exc:
        print(f"Postgres unavailable: {exc}")
        return

    redis_client = None
    try:
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
    except Exception as exc:
        print(f"Redis unavailable, continuing with postgres only: {exc}")

    anomaly_count = 0
    for item in results:
        cur.execute(
            """
            INSERT INTO coin_snapshots (
                coin_id, symbol, name, current_price, market_cap, market_cap_rank, total_volume,
                high_24h, low_24h, price_change_percentage_24h, price_change_percentage_1h,
                high_low_range_pct, volume_to_market_cap, price_vs_high_24h, price_vs_low_24h,
                circulating_supply, anomaly_score, is_anomaly, severity, ingested_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                item.get("coin_id"),
                item.get("symbol"),
                item.get("name"),
                item.get("current_price"),
                int(item.get("market_cap") or 0),
                int(item.get("market_cap_rank") or 999),
                int(item.get("total_volume") or 0),
                item.get("high_24h"),
                item.get("low_24h"),
                item.get("price_change_percentage_24h"),
                item.get("price_change_percentage_1h"),
                item.get("high_low_range_pct"),
                item.get("volume_to_market_cap"),
                item.get("price_vs_high_24h"),
                item.get("price_vs_low_24h"),
                item.get("circulating_supply"),
                item.get("anomaly_score"),
                item.get("is_anomaly"),
                item.get("severity"),
                item.get("ingested_at"),
            ),
        )

        if item.get("is_anomaly"):
            anomaly_count += 1
            cur.execute(
                """
                INSERT INTO anomalies (
                    coin_id, symbol, name, current_price, anomaly_score, severity,
                    price_change_percentage_24h, price_change_percentage_1h,
                    total_volume, volume_to_market_cap
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    item.get("coin_id"),
                    item.get("symbol"),
                    item.get("name"),
                    item.get("current_price"),
                    item.get("anomaly_score"),
                    item.get("severity"),
                    item.get("price_change_percentage_24h"),
                    item.get("price_change_percentage_1h"),
                    int(item.get("total_volume") or 0),
                    item.get("volume_to_market_cap"),
                ),
            )

        if redis_client is not None:
            pipe = redis_client.pipeline()
            pipe.lpush("stats:recent_coins", json.dumps(item))
            pipe.ltrim("stats:recent_coins", 0, 99)
            pipe.set(f"stats:{item.get('coin_id')}:last_price", item.get("current_price"))
            pipe.set(f"stats:{item.get('coin_id')}:last_score", item.get("anomaly_score"))
            if item.get("is_anomaly"):
                pipe.lpush("stats:recent_anomalies", json.dumps(item))
                pipe.ltrim("stats:recent_anomalies", 0, 19)
            for key in [
                "stats:recent_coins",
                "stats:recent_anomalies",
                f"stats:{item.get('coin_id')}:last_price",
                f"stats:{item.get('coin_id')}:last_score",
            ]:
                pipe.expire(key, 86400)
            pipe.execute()

    if redis_client is not None:
        pipe = redis_client.pipeline()
        pipe.incr("stats:total_snapshots", len(results))
        pipe.incr("stats:total_anomalies", anomaly_count)
        pipe.set("stats:last_updated", datetime.utcnow().isoformat() + "Z")
        for key in ["stats:total_snapshots", "stats:total_anomalies", "stats:last_updated"]:
            pipe.expire(key, 86400)
        pipe.execute()

    conn.commit()
    cur.close()
    conn.close()
    print(f"epoch {epoch_id}: processed {len(results)} records, anomalies={anomaly_count}")


def main() -> None:
    wait_for_services()
    spark = (
        SparkSession.builder.appName("StreamIQCrypto")
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
        .getOrCreate()
    )

    schema = StructType(
        [
            StructField("coin_id", StringType()),
            StructField("symbol", StringType()),
            StructField("name", StringType()),
            StructField("current_price", DoubleType()),
            StructField("market_cap", DoubleType()),
            StructField("market_cap_rank", IntegerType()),
            StructField("total_volume", DoubleType()),
            StructField("high_24h", DoubleType()),
            StructField("low_24h", DoubleType()),
            StructField("price_change_24h", DoubleType()),
            StructField("price_change_percentage_24h", DoubleType()),
            StructField("price_change_percentage_1h", DoubleType()),
            StructField("circulating_supply", DoubleType()),
            StructField("high_low_range_pct", DoubleType()),
            StructField("volume_to_market_cap", DoubleType()),
            StructField("price_vs_high_24h", DoubleType()),
            StructField("price_vs_low_24h", DoubleType()),
            StructField("last_updated", StringType()),
            StructField("ingested_at", StringType()),
        ]
    )

    stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = stream.select(from_json(col("value").cast("string"), schema).alias("d")).select("d.*")
    query = parsed.writeStream.foreachBatch(process_batch).trigger(processingTime="30 seconds").start()
    query.awaitTermination()


if __name__ == "__main__":
    main()
