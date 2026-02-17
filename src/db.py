"""
Database helper — manages PostgreSQL connections and inserts.
"""

import psycopg2
from psycopg2.extras import execute_values

from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection using settings from config."""
    return psycopg2.connect(**DB_CONFIG)


def insert_reading(reading: dict) -> None:
    """Insert a single heartbeat reading into the database."""
    sql = """
        INSERT INTO heartbeat_readings (customer_id, heart_rate, recorded_at, is_anomaly)
        VALUES (%(customer_id)s, %(heart_rate)s, %(timestamp)s, %(is_anomaly)s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, reading)
        conn.commit()
    finally:
        conn.close()


def insert_readings_batch(readings: list[dict]) -> None:
    """Insert multiple heartbeat readings in a single round-trip."""
    sql = """
        INSERT INTO heartbeat_readings (customer_id, heart_rate, recorded_at, is_anomaly)
        VALUES %s
    """
    values = [
        (r["customer_id"], r["heart_rate"], r["timestamp"], r["is_anomaly"])
        for r in readings
    ]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, values)
        conn.commit()
    finally:
        conn.close()


def query_latest_readings(limit: int = 20) -> list[tuple]:
    """Fetch the most recent heartbeat readings."""
    sql = """
        SELECT customer_id, heart_rate, recorded_at, is_anomaly
        FROM heartbeat_readings
        ORDER BY recorded_at DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def query_anomalies(limit: int = 20) -> list[tuple]:
    """Fetch the most recent anomaly readings."""
    sql = """
        SELECT customer_id, heart_rate, recorded_at
        FROM heartbeat_readings
        WHERE is_anomaly = TRUE
        ORDER BY recorded_at DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_customer_stats() -> list[tuple]:
    """Return per-customer aggregated stats."""
    sql = """
        SELECT
            customer_id,
            COUNT(*)            AS total_readings,
            ROUND(AVG(heart_rate), 1) AS avg_hr,
            MIN(heart_rate)     AS min_hr,
            MAX(heart_rate)     AS max_hr,
            SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) AS anomaly_count
        FROM heartbeat_readings
        GROUP BY customer_id
        ORDER BY customer_id
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


# ── Quick standalone test ──────────────────────────────────────
if __name__ == "__main__":
    print("[DB] Testing connection...")
    conn = get_connection()
    print("[DB] Connected successfully!")
    conn.close()

    rows = query_latest_readings(5)
    print(f"[DB] Latest {len(rows)} readings:")
    for row in rows:
        print(f"  {row}")
