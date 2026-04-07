import json
import os
import time
from datetime import datetime

import requests
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-broker:9092")
TOPIC = "crypto_prices"
POLL_INTERVAL = 30
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
    "&sparkline=false&price_change_percentage=1h,24h"
)


def wait_for_kafka(max_retries: int = 30) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            admin = KafkaAdminClient(bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS])
            admin.close()
            print("Kafka is ready.")
            return
        except Exception:
            print(f"Waiting for Kafka... attempt {attempt}/{max_retries}")
            time.sleep(3)
    raise RuntimeError("Kafka not available after retries")


def build_payload(coin: dict) -> dict:
    high = coin.get("high_24h") or coin.get("current_price") or 1
    low = coin.get("low_24h") or coin.get("current_price") or 1
    price = coin.get("current_price") or 1
    market_cap = coin.get("market_cap") or 1
    volume = coin.get("total_volume") or 0
    return {
        "coin_id": coin["id"],
        "symbol": coin.get("symbol", "").upper(),
        "name": coin.get("name", ""),
        "current_price": price,
        "market_cap": market_cap,
        "market_cap_rank": coin.get("market_cap_rank") or 999,
        "total_volume": volume,
        "high_24h": high,
        "low_24h": low,
        "price_change_24h": coin.get("price_change_24h") or 0,
        "price_change_percentage_24h": coin.get("price_change_percentage_24h") or 0,
        "price_change_percentage_1h": coin.get("price_change_percentage_1h_in_currency") or 0,
        "circulating_supply": coin.get("circulating_supply") or 0,
        "high_low_range_pct": round((high - low) / price * 100, 4) if price else 0,
        "volume_to_market_cap": round(volume / market_cap, 6) if market_cap else 0,
        "price_vs_high_24h": round((price - high) / high * 100, 4) if high else 0,
        "price_vs_low_24h": round((price - low) / low * 100, 4) if low else 0,
        "last_updated": coin.get("last_updated"),
        "ingested_at": datetime.utcnow().isoformat(),
    }


def main() -> None:
    wait_for_kafka()
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    while True:
        try:
            response = requests.get(COINGECKO_URL, timeout=10)
            if response.status_code == 429:
                print("Rate limited by CoinGecko. Waiting 60s...")
                time.sleep(60)
                continue

            response.raise_for_status()
            coins = response.json()
            for coin in coins:
                producer.send(TOPIC, build_payload(coin))
            producer.flush()
            print(f"Produced {len(coins)} coins at {datetime.utcnow().isoformat()}")
        except requests.RequestException as exc:
            print(f"CoinGecko fetch error: {exc}. Retrying in 30s...")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
