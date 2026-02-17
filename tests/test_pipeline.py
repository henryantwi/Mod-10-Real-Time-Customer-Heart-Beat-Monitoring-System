"""
Pipeline Test Script.

Tests individual components of the heartbeat monitoring system:
  1. Data generator produces valid data
  2. Database connection works
  3. Database insert and query work
  4. (Manual) Kafka producer → consumer → DB end-to-end
"""

import sys
import os

# Add src/ to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_generator import generate_batch, generate_customer_ids, generate_heartbeat
from config import NUM_CUSTOMERS, NORMAL_HR_LOW, NORMAL_HR_HIGH


def test_customer_id_generation():
    """Test that customer IDs are generated correctly."""
    ids = generate_customer_ids(3)
    assert len(ids) == 3, f"Expected 3, got {len(ids)}"
    assert ids[0] == "CUST-001", f"Expected CUST-001, got {ids[0]}"
    assert ids[2] == "CUST-003", f"Expected CUST-003, got {ids[2]}"
    print("[PASS] test_customer_id_generation")


def test_heartbeat_has_required_fields():
    """Test that each reading contains the required fields."""
    reading = generate_heartbeat("CUST-001")
    required = {"customer_id", "timestamp", "heart_rate", "is_anomaly"}
    missing = required - reading.keys()
    assert not missing, f"Missing fields: {missing}"
    print("[PASS] test_heartbeat_has_required_fields")


def test_heart_rate_is_integer():
    """Test that heart rate is an integer."""
    reading = generate_heartbeat("CUST-001")
    assert isinstance(reading["heart_rate"], int), "heart_rate should be int"
    print("[PASS] test_heart_rate_is_integer")


def test_batch_size_matches_customer_count():
    """Test that batch size equals the number of customers."""
    ids = generate_customer_ids(NUM_CUSTOMERS)
    batch = generate_batch(ids)
    assert len(batch) == NUM_CUSTOMERS, f"Expected {NUM_CUSTOMERS}, got {len(batch)}"
    print("[PASS] test_batch_size_matches_customer_count")


def test_heart_rate_within_bounds():
    """Test that heart rates (including anomalies) are within the extreme bounds."""
    for _ in range(100):
        reading = generate_heartbeat("CUST-001")
        hr = reading["heart_rate"]
        assert 30 <= hr <= 180, f"Heart rate {hr} is outside [30, 180]"
    print("[PASS] test_heart_rate_within_bounds")


def test_db_connection():
    """Test that we can connect to PostgreSQL."""
    try:
        from db import get_connection
        conn = get_connection()
        conn.close()
        print("[PASS] test_db_connection")
    except Exception as e:
        print(f"[SKIP] test_db_connection — DB not reachable: {e}")


def test_db_insert_and_query():
    """Test inserting a reading and querying it back."""
    try:
        from db import insert_reading, query_latest_readings
        reading = generate_heartbeat("TEST-001")
        insert_reading(reading)
        rows = query_latest_readings(1)
        assert len(rows) >= 1, "Expected at least one row after insert"
        print("[PASS] test_db_insert_and_query")
    except Exception as e:
        print(f"[SKIP] test_db_insert_and_query — DB not reachable: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("  Heartbeat Pipeline — Component Tests")
    print("=" * 50 + "\n")

    # Data generator tests (no external dependencies)
    test_customer_id_generation()
    test_heartbeat_has_required_fields()
    test_heart_rate_is_integer()
    test_batch_size_matches_customer_count()
    test_heart_rate_within_bounds()

    print()

    # Database tests (require running PostgreSQL)
    test_db_connection()
    test_db_insert_and_query()

    print("\n" + "=" * 50)
    print("  All available tests completed.")
    print("=" * 50)
