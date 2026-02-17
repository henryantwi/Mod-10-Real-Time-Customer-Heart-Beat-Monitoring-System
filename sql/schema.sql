-- ============================================================
-- Heartbeat Monitoring System — Database Schema
-- ============================================================

-- Table to store customer heartbeat readings
CREATE TABLE IF NOT EXISTS heartbeat_readings (
    id              SERIAL PRIMARY KEY,
    customer_id     VARCHAR(20)      NOT NULL,
    heart_rate      INTEGER          NOT NULL,
    recorded_at     TIMESTAMPTZ      NOT NULL,
    is_anomaly      BOOLEAN          DEFAULT FALSE,
    created_at      TIMESTAMPTZ      DEFAULT NOW()
);

-- Index on timestamp for efficient time-range queries
CREATE INDEX IF NOT EXISTS idx_heartbeat_recorded_at
    ON heartbeat_readings (recorded_at);

-- Index on customer_id for per-customer lookups
CREATE INDEX IF NOT EXISTS idx_heartbeat_customer_id
    ON heartbeat_readings (customer_id);

-- Composite index for queries that filter by customer + time range
CREATE INDEX IF NOT EXISTS idx_heartbeat_customer_time
    ON heartbeat_readings (customer_id, recorded_at);
