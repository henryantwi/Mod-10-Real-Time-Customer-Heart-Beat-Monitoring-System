from config import (
    ANOMALY_CHANCE,
    ANOMALY_HR_HIGH,
    ANOMALY_HR_LOW,
    DB_CONFIG,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    NORMAL_HR_HIGH,
    NORMAL_HR_LOW,
    NUM_CUSTOMERS,
    SEND_INTERVAL_SECONDS,
)


def test_kafka_bootstrap_servers_is_string():
    assert isinstance(KAFKA_BOOTSTRAP_SERVERS, str)


def test_kafka_topic_is_string():
    assert isinstance(KAFKA_TOPIC, str)
    assert len(KAFKA_TOPIC) > 0


def test_db_config_has_required_keys():
    required_keys = {"host", "port", "database", "user", "password"}
    assert required_keys.issubset(DB_CONFIG.keys())


def test_db_config_port_is_int():
    assert isinstance(DB_CONFIG["port"], int)


def test_num_customers_positive():
    assert NUM_CUSTOMERS > 0


def test_send_interval_positive():
    assert SEND_INTERVAL_SECONDS > 0


def test_normal_hr_range_valid():
    assert NORMAL_HR_LOW > 0
    assert NORMAL_HR_HIGH > 0
    assert NORMAL_HR_LOW < NORMAL_HR_HIGH


def test_anomaly_hr_range_valid():
    assert ANOMALY_HR_LOW < ANOMALY_HR_HIGH


def test_anomaly_hr_contains_normal():
    assert ANOMALY_HR_LOW <= NORMAL_HR_LOW
    assert ANOMALY_HR_HIGH >= NORMAL_HR_HIGH


def test_anomaly_chance_is_probability():
    assert 0 <= ANOMALY_CHANCE <= 1
