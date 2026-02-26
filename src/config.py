"""
Centralized configuration for the Heartbeat Monitoring System.
All connection strings, topic names, and tunables live here.
"""

# ── Kafka Settings ─────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS = "127.0.0.1:9092"
KAFKA_TOPIC = "heartbeat-readings"

# ── PostgreSQL Settings ────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "heartbeat_db",
    "user": "heartbeat_user",
    "password": "heartbeat_pass",
}

# ── Data Generator Settings ────────────────────────────────────
NUM_CUSTOMERS = 5  # Number of simulated customers
SEND_INTERVAL_SECONDS = 1  # Delay between each reading batch
NORMAL_HR_LOW = 60  # Normal resting heart rate lower bound
NORMAL_HR_HIGH = 100  # Normal resting heart rate upper bound
ANOMALY_HR_LOW = 30  # Possible anomaly lower bound
ANOMALY_HR_HIGH = 180  # Possible anomaly upper bound
ANOMALY_CHANCE = 0.05  # 5 % chance of generating an anomaly reading
