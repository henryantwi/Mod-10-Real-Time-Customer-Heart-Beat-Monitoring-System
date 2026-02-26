"""Unit tests for kafka_consumer module."""

import json
from unittest.mock import MagicMock, patch

from kafka_consumer import create_consumer, flag_anomaly, run_consumer, validate_reading


class TestValidateReading:
    """Tests for validate_reading()."""

    def test_validate_reading_valid(self, sample_reading):
        assert validate_reading(sample_reading) is True

    def test_validate_reading_missing_customer_id(self, sample_reading):
        del sample_reading["customer_id"]
        assert validate_reading(sample_reading) is False

    def test_validate_reading_missing_timestamp(self, sample_reading):
        del sample_reading["timestamp"]
        assert validate_reading(sample_reading) is False

    def test_validate_reading_missing_heart_rate(self, sample_reading):
        del sample_reading["heart_rate"]
        assert validate_reading(sample_reading) is False

    def test_validate_reading_invalid_hr_type_string(self, invalid_hr_reading):
        invalid_hr_reading["heart_rate"] = "abc"
        assert validate_reading(invalid_hr_reading) is False

    def test_validate_reading_hr_float_accepted(self, sample_reading):
        sample_reading["heart_rate"] = 72.5
        assert validate_reading(sample_reading) is True

    def test_validate_reading_empty_dict(self):
        assert validate_reading({}) is False


class TestFlagAnomaly:
    """Tests for flag_anomaly()."""

    def test_flag_anomaly_normal_hr(self, sample_reading):
        sample_reading["heart_rate"] = 72
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is False

    def test_flag_anomaly_low_hr(self, sample_reading):
        sample_reading["heart_rate"] = 50
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is True

    def test_flag_anomaly_high_hr(self, sample_reading):
        sample_reading["heart_rate"] = 110
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is True

    def test_flag_anomaly_boundary_low(self, sample_reading):
        sample_reading["heart_rate"] = 60
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is False

    def test_flag_anomaly_boundary_high(self, sample_reading):
        sample_reading["heart_rate"] = 100
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is False

    def test_flag_anomaly_just_below_low(self, sample_reading):
        sample_reading["heart_rate"] = 59
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is True

    def test_flag_anomaly_just_above_high(self, sample_reading):
        sample_reading["heart_rate"] = 101
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is True

    def test_flag_anomaly_overrides_existing(self, sample_reading):
        sample_reading["heart_rate"] = 72
        sample_reading["is_anomaly"] = True
        result = flag_anomaly(sample_reading)
        assert result["is_anomaly"] is False


class TestCreateConsumer:
    """Tests for create_consumer()."""

    @patch("kafka_consumer.Consumer")
    def test_create_consumer_returns_consumer(self, mock_consumer_cls):
        mock_instance = MagicMock()
        mock_consumer_cls.return_value = mock_instance
        result = create_consumer()
        mock_consumer_cls.assert_called_once()
        assert result is mock_instance

    @patch("kafka_consumer.Consumer")
    def test_create_consumer_config(self, mock_consumer_cls):
        create_consumer()
        call_args = mock_consumer_cls.call_args[0][0]
        assert call_args["bootstrap.servers"] == "127.0.0.1:9092"
        assert call_args["group.id"] == "heartbeat-consumer-group"
        assert call_args["auto.offset.reset"] == "earliest"


class TestRunConsumer:
    """Tests for run_consumer() with mocked Kafka and DB."""

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_processes_valid_message(self, mock_create, mock_insert):
        """Test that a valid message is processed and stored."""
        reading = {
            "customer_id": "CUST-001",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "heart_rate": 72,
            "is_anomaly": False,
        }
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = json.dumps(reading).encode("utf-8")

        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()

        mock_insert.assert_called_once()
        mock_consumer.close.assert_called_once()

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_skips_none_message(self, mock_create, mock_insert):
        """Test that None messages are skipped."""
        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [None, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()

        mock_insert.assert_not_called()

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_skips_invalid_reading(self, mock_create, mock_insert):
        """Test that invalid readings are skipped."""
        invalid = {"customer_id": "CUST-001"}  # missing fields
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = json.dumps(invalid).encode("utf-8")

        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()

        mock_insert.assert_not_called()

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_handles_db_error(self, mock_create, mock_insert):
        """Test that DB errors are logged but don't crash the consumer."""
        reading = {
            "customer_id": "CUST-001",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "heart_rate": 72,
            "is_anomaly": False,
        }
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = json.dumps(reading).encode("utf-8")

        mock_insert.side_effect = Exception("DB connection failed")

        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()  # should not raise

        mock_consumer.close.assert_called_once()

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_handles_partition_eof(self, mock_create, mock_insert):
        """Test that partition EOF errors are handled gracefully."""
        from confluent_kafka import KafkaError as KE

        mock_error = MagicMock()
        mock_error.code.return_value = KE._PARTITION_EOF

        mock_msg = MagicMock()
        mock_msg.error.return_value = mock_error

        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()

        mock_insert.assert_not_called()

    @patch("kafka_consumer.insert_reading")
    @patch("kafka_consumer.create_consumer")
    def test_run_consumer_handles_kafka_error(self, mock_create, mock_insert):
        """Test that non-EOF Kafka errors are logged and skipped."""
        mock_error = MagicMock()
        mock_error.code.return_value = -1  # some error code

        mock_msg = MagicMock()
        mock_msg.error.return_value = mock_error

        mock_consumer = MagicMock()
        mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt]
        mock_create.return_value = mock_consumer

        run_consumer()

        mock_insert.assert_not_called()
