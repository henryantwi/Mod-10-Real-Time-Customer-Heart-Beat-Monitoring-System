"""
Kafka Consumer — reads heartbeat messages from Kafka and writes them to PostgreSQL.

Includes basic validation:
  • Rejects readings with missing fields.
  • Flags anomalies where heart rate is outside the normal 60–100 bpm range.
"""

import json
import sys

from kafka import KafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, NORMAL_HR_HIGH, NORMAL_HR_LOW
from db import insert_reading

REQUIRED_FIELDS = {"customer_id", "timestamp", "heart_rate"}


def validate_reading(reading: dict) -> bool:
    """Return True if the reading has all required fields and valid types."""
    if not REQUIRED_FIELDS.issubset(reading.keys()):
        print(f"  [SKIP] Missing fields: {REQUIRED_FIELDS - reading.keys()}")
        return False

    if not isinstance(reading["heart_rate"], (int, float)):
        print(f"  [SKIP] Invalid heart_rate type: {type(reading['heart_rate'])}")
        return False

    return True


def flag_anomaly(reading: dict) -> dict:
    """
    Set is_anomaly based on whether heart rate falls outside the normal range.
    This overrides whatever the generator set, acting as a server-side check.
    """
    hr = reading["heart_rate"]
    reading["is_anomaly"] = hr < NORMAL_HR_LOW or hr > NORMAL_HR_HIGH
    return reading


def create_consumer() -> KafkaConsumer:
    """Create and return a KafkaConsumer that deserializes JSON messages."""
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="heartbeat-consumer-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )


def run_consumer():
    """Main loop — consumes messages, validates, and stores in PostgreSQL."""
    consumer = create_consumer()

    print(f"[Consumer] Listening on topic: {KAFKA_TOPIC}")
    print(f"[Consumer] Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}\n")

    message_count = 0
    stored_count = 0

    try:
        for message in consumer:
            reading = message.value
            message_count += 1

            # Validate
            if not validate_reading(reading):
                continue

            # Server-side anomaly check
            reading = flag_anomaly(reading)

            # Store in PostgreSQL
            try:
                insert_reading(reading)
                stored_count += 1
                flag = " ⚠ ANOMALY" if reading["is_anomaly"] else ""
                print(
                    f"  [Stored #{stored_count}] "
                    f"{reading['customer_id']}  HR={reading['heart_rate']:>3}"
                    f"  @ {reading['timestamp']}{flag}"
                )
            except Exception as e:
                print(f"  [ERROR] Failed to store reading: {e}")

    except KeyboardInterrupt:
        print(f"\n[Consumer] Stopped. Messages received: {message_count}, Stored: {stored_count}")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
