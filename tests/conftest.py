"""
Shared fixtures and configuration for the test suite.
"""

import pytest

from data_generator import generate_heartbeat


@pytest.fixture
def sample_reading():
    """A single valid heartbeat reading."""
    return {
        "customer_id": "CUST-001",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "heart_rate": 72,
        "is_anomaly": False,
    }


@pytest.fixture
def sample_anomaly_reading():
    """A single anomaly heartbeat reading."""
    return {
        "customer_id": "CUST-002",
        "timestamp": "2026-01-01T00:00:01+00:00",
        "heart_rate": 185,
        "is_anomaly": True,
    }


@pytest.fixture
def sample_customer_ids():
    """A list of sample customer IDs."""
    return ["CUST-001", "CUST-002", "CUST-003"]


@pytest.fixture
def sample_batch(sample_customer_ids):
    """A batch of heartbeat readings, one per customer."""
    return [generate_heartbeat(cid) for cid in sample_customer_ids]


@pytest.fixture
def incomplete_reading():
    """A reading missing required fields."""
    return {
        "customer_id": "CUST-001",
        "timestamp": "2026-01-01T00:00:00+00:00",
        # heart_rate intentionally missing
    }


@pytest.fixture
def invalid_hr_reading():
    """A reading with an invalid heart_rate type."""
    return {
        "customer_id": "CUST-001",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "heart_rate": "not-a-number",
        "is_anomaly": False,
    }
