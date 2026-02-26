from datetime import datetime
from unittest.mock import patch

from data_generator import generate_batch, generate_customer_ids, generate_heartbeat


class TestGenerateCustomerIds:
    def test_generate_customer_ids_count(self):
        for n in [1, 3, 5, 10]:
            assert len(generate_customer_ids(n)) == n

    def test_generate_customer_ids_format(self):
        ids = generate_customer_ids(3)
        assert ids == ["CUST-001", "CUST-002", "CUST-003"]

    def test_generate_customer_ids_zero(self):
        assert generate_customer_ids(0) == []

    def test_generate_customer_ids_large(self):
        ids = generate_customer_ids(100)
        assert len(ids) == 100
        assert ids[0] == "CUST-001"
        assert ids[99] == "CUST-100"


class TestGenerateHeartbeat:
    def test_heartbeat_has_required_fields(self):
        result = generate_heartbeat("CUST-001")
        assert "customer_id" in result
        assert "timestamp" in result
        assert "heart_rate" in result
        assert "is_anomaly" in result

    def test_heartbeat_customer_id_matches(self):
        result = generate_heartbeat("CUST-042")
        assert result["customer_id"] == "CUST-042"

    def test_heartbeat_heart_rate_is_integer(self):
        result = generate_heartbeat("CUST-001")
        assert isinstance(result["heart_rate"], int)

    def test_heartbeat_timestamp_is_iso_format(self):
        result = generate_heartbeat("CUST-001")
        parsed = datetime.fromisoformat(result["timestamp"])
        assert isinstance(parsed, datetime)

    @patch("data_generator.random.random", return_value=1.0)
    def test_heartbeat_normal_path(self, mock_random):
        result = generate_heartbeat("CUST-001")
        assert result["is_anomaly"] is False
        assert 60 <= result["heart_rate"] <= 100

    @patch("data_generator.random.random", return_value=0.0)
    def test_heartbeat_anomaly_path(self, mock_random):
        result = generate_heartbeat("CUST-001")
        assert result["is_anomaly"] is True
        assert 30 <= result["heart_rate"] <= 180

    def test_heart_rate_within_bounds(self):
        for _ in range(200):
            result = generate_heartbeat("CUST-001")
            assert 30 <= result["heart_rate"] <= 180


class TestGenerateBatch:
    def test_batch_size_matches(self):
        ids = ["CUST-001", "CUST-002", "CUST-003"]
        batch = generate_batch(ids)
        assert len(batch) == len(ids)

    def test_batch_customer_ids_match(self):
        ids = ["CUST-001", "CUST-002", "CUST-003"]
        batch = generate_batch(ids)
        for reading, expected_id in zip(batch, ids, strict=True):
            assert reading["customer_id"] == expected_id
