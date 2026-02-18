"""
Database helper — manages PostgreSQL connections and inserts.
"""

import pg8000.dbapi

from config import DB_CONFIG


def get_connection():
    """Return a new pg8000 connection using settings from config."""
    return pg8000.dbapi.connect(**DB_CONFIG)


def insert_reading(reading: dict) -> None:
    """Insert a single heartbeat reading into the database."""
    sql = """
        INSERT INTO heartbeat_readings (customer_id, heart_rate, recorded_at, is_anomaly)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        reading["customer_id"],
        reading["heart_rate"],
        reading["timestamp"],
        reading["is_anomaly"],
    )
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()


def insert_readings_batch(readings: list[dict]) -> None:
    """Insert multiple heartbeat readings."""
    sql = """
        INSERT INTO heartbeat_readings (customer_id, heart_rate, recorded_at, is_anomaly)
        VALUES (%s, %s, %s, %s)
    """
    # pg8000 executemany creates many INSERT statements, but it works
    params_list = [
        (r["customer_id"], r["heart_rate"], r["timestamp"], r["is_anomaly"])
        for r in readings
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()


def query_latest_readings(limit: int = 20) -> list[tuple]:
    """Fetch the most recent heartbeat readings."""
    sql = """
        SELECT customer_id, heart_rate, recorded_at, is_anomaly
        FROM heartbeat_readings
        ORDER BY recorded_at DESC
        LIMIT %s
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        return cursor.fetchall()


def query_anomalies(limit: int = 20) -> list[tuple]:
    """Fetch the most recent anomaly readings."""
    sql = """
        SELECT customer_id, heart_rate, recorded_at
        FROM heartbeat_readings
        WHERE is_anomaly = TRUE
        ORDER BY recorded_at DESC
        LIMIT %s
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        return cursor.fetchall()


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
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()


# ── Quick standalone test ──────────────────────────────────────
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("[DB] Testing connection...")
    try:
        conn = get_connection()
        logging.info("[DB] Connected successfully!")
        conn.close()

        logging.info("[DB] Querying latest readings...")
        rows = query_latest_readings(5)
        logging.info(f"[DB] Latest {len(rows)} readings:")
        for row in rows:
            logging.info(f"  {row}")
    except Exception as e:
        logging.error(f"[DB] Connection query failed: {e}")
