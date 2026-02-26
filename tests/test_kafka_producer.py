"""Unit tests for the Kafka producer module."""

import json
from unittest.mock import MagicMock, patch

from kafka_producer import create_producer, run_producer


class TestCreateProducer:
    """Tests for the create_producer function."""

    @patch("kafka_producer.Producer")
    def test_create_producer_returns_producer(self, mock_producer_cls):
        """Patch confluent_kafka.Producer and verify create_producer calls it."""
        mock_instance = MagicMock()
        mock_producer_cls.return_value = mock_instance

        result = create_producer()

        mock_producer_cls.assert_called_once_with({"bootstrap.servers": "127.0.0.1:9092"})
        assert result is mock_instance


class TestReadingSerialization:
    """Tests for the serialization pattern used by the producer."""

    def test_reading_serialization(self, sample_reading):
        """Verify a heartbeat reading dict serializes to valid JSON bytes."""
        serialized = json.dumps(sample_reading).encode("utf-8")

        assert isinstance(serialized, bytes)
        # Round-trip through JSON to confirm it's valid
        parsed = json.loads(serialized)
        assert parsed == sample_reading

    def test_serialized_reading_deserializes(self, sample_reading):
        """Round-trip: serialize then deserialize, verify fields match."""
        serialized = json.dumps(sample_reading).encode("utf-8")
        deserialized = json.loads(serialized.decode("utf-8"))

        assert deserialized["customer_id"] == sample_reading["customer_id"]
        assert deserialized["timestamp"] == sample_reading["timestamp"]
        assert deserialized["heart_rate"] == sample_reading["heart_rate"]
        assert deserialized["is_anomaly"] == sample_reading["is_anomaly"]

    def test_serialized_reading_contains_required_fields(self, sample_reading):
        """Serialized JSON has customer_id, timestamp, heart_rate, is_anomaly."""
        serialized = json.dumps(sample_reading).encode("utf-8")
        parsed = json.loads(serialized)

        required_fields = {"customer_id", "timestamp", "heart_rate", "is_anomaly"}
        assert required_fields.issubset(parsed.keys())


class TestRunProducer:
    """Tests for run_producer() with mocked Kafka."""

    @patch("kafka_producer.time")
    @patch("kafka_producer.create_producer")
    def test_run_producer_sends_messages(self, mock_create, mock_time):
        """Test that producer sends messages and flushes."""
        mock_producer = MagicMock()
        mock_create.return_value = mock_producer
        mock_time.sleep.side_effect = KeyboardInterrupt

        run_producer()

        assert mock_producer.produce.called
        assert mock_producer.flush.called
        mock_producer.flush.assert_called()

    @patch("kafka_producer.time")
    @patch("kafka_producer.create_producer")
    def test_run_producer_serializes_as_json(self, mock_create, mock_time):
        """Test that messages are serialized as JSON bytes."""
        mock_producer = MagicMock()
        mock_create.return_value = mock_producer
        mock_time.sleep.side_effect = KeyboardInterrupt

        run_producer()

        # Check that produce was called with bytes that decode to valid JSON
        for call in mock_producer.produce.call_args_list:
            val_bytes = call.kwargs.get("value") or call.args[1]
            parsed = json.loads(val_bytes.decode("utf-8"))
            assert "customer_id" in parsed
            assert "heart_rate" in parsed

    @patch("kafka_producer.time")
    @patch("kafka_producer.create_producer")
    def test_run_producer_closes_on_interrupt(self, mock_create, mock_time):
        """Test that producer flushes on KeyboardInterrupt."""
        mock_producer = MagicMock()
        mock_create.return_value = mock_producer
        mock_time.sleep.side_effect = KeyboardInterrupt

        run_producer()

        # flush should be called in the finally block
        assert mock_producer.flush.call_count >= 1
