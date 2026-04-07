CREATE TABLE IF NOT EXISTS coin_snapshots (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50),
    symbol VARCHAR(20),
    name VARCHAR(100),
    current_price DOUBLE PRECISION,
    market_cap BIGINT,
    market_cap_rank INTEGER,
    total_volume BIGINT,
    high_24h DOUBLE PRECISION,
    low_24h DOUBLE PRECISION,
    price_change_percentage_24h DOUBLE PRECISION,
    price_change_percentage_1h DOUBLE PRECISION,
    high_low_range_pct DOUBLE PRECISION,
    volume_to_market_cap DOUBLE PRECISION,
    price_vs_high_24h DOUBLE PRECISION,
    price_vs_low_24h DOUBLE PRECISION,
    circulating_supply DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    is_anomaly BOOLEAN,
    severity VARCHAR(10),
    ingested_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50),
    symbol VARCHAR(20),
    name VARCHAR(100),
    current_price DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    severity VARCHAR(10),
    price_change_percentage_24h DOUBLE PRECISION,
    price_change_percentage_1h DOUBLE PRECISION,
    total_volume BIGINT,
    volume_to_market_cap DOUBLE PRECISION,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_coin_id ON coin_snapshots(coin_id);
CREATE INDEX idx_snapshots_processed_at ON coin_snapshots(processed_at DESC);
CREATE INDEX idx_snapshots_is_anomaly ON coin_snapshots(is_anomaly);
CREATE INDEX idx_anomalies_detected_at ON anomalies(detected_at DESC);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
CREATE INDEX idx_anomalies_coin_id ON anomalies(coin_id);
