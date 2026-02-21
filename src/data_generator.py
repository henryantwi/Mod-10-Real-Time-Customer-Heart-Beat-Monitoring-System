"""
Synthetic Heartbeat Data Generator.

Produces realistic heart rate readings for a set of simulated customers.
Each reading is a dictionary with customer_id, timestamp, and heart_rate.
"""

import random
import time
from datetime import datetime, timezone

from config import (
    ANOMALY_CHANCE,
    ANOMALY_HR_HIGH,
    ANOMALY_HR_LOW,
    NORMAL_HR_HIGH,
    NORMAL_HR_LOW,
    NUM_CUSTOMERS,
)


def generate_customer_ids(n: int) -> list[str]:
    """Create a list of customer IDs like CUST-001, CUST-002, etc."""
    return [f"CUST-{str(i).zfill(3)}" for i in range(1, n + 1)]


def generate_heartbeat(customer_id: str) -> dict:
    """
    Generate a single heartbeat reading for the given customer.

    Returns a dict: { customer_id, timestamp, heart_rate, is_anomaly }
    """
    # Decide if this reading is anomalous
    is_anomaly = random.random() < ANOMALY_CHANCE

    if is_anomaly:
        heart_rate = random.randint(ANOMALY_HR_LOW, ANOMALY_HR_HIGH)
    else:
        heart_rate = random.randint(NORMAL_HR_LOW, NORMAL_HR_HIGH)

    return {
        "customer_id": customer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": heart_rate,
        "is_anomaly": is_anomaly,
    }


def generate_batch(customer_ids: list[str]) -> list[dict]:
    """Generate one reading per customer."""
    return [generate_heartbeat(cid) for cid in customer_ids]


# ── Quick standalone test ──────────────────────────────────────
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    customers = generate_customer_ids(NUM_CUSTOMERS)
    logging.info(f"Simulating {len(customers)} customers: {customers}\n")

    for _ in range(3):  # Generate 3 batches for demo
        batch = generate_batch(customers)
        for reading in batch:
            flag = " ⚠ ANOMALY" if reading["is_anomaly"] else ""
            logging.info(f"  {reading['customer_id']}  HR={reading['heart_rate']:>3}{flag}")
        logging.info("")
        time.sleep(1)
