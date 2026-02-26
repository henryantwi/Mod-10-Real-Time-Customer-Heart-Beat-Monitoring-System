"""
Kafka Producer — sends heartbeat readings to a Kafka topic.

Continuously generates data and publishes JSON messages to the
configured Kafka topic at a regular interval.
"""

import json
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from confluent_kafka import Producer  # noqa: E402

from config import (  # noqa: E402
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    NUM_CUSTOMERS,
    SEND_INTERVAL_SECONDS,
)
from data_generator import generate_batch, generate_customer_ids  # noqa: E402


def create_producer() -> Producer:
    """Create and return a KafkaProducer that serializes values as JSON."""
    return Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


def run_producer():
    """Main loop — generates heartbeat data and sends it to Kafka."""
    producer = create_producer()
    customer_ids = generate_customer_ids(NUM_CUSTOMERS)

    logging.info(f"[Producer] Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
    logging.info(f"[Producer] Publishing to topic: {KAFKA_TOPIC}")
    logging.info(f"[Producer] Simulating {len(customer_ids)} customers")

    message_count = 0

    def delivery_report(err, msg):
        if err is not None:
            logging.error(f"Message delivery failed: {err}")

    # Continuously generate and send batches of readings
    try:
        while True:
            batch = generate_batch(customer_ids)
            for reading in batch:
                val_bytes = json.dumps(reading).encode("utf-8")
                producer.produce(KAFKA_TOPIC, value=val_bytes, callback=delivery_report)
                producer.poll(0)
                message_count += 1

                flag = " [ANOMALY]" if reading["is_anomaly"] else ""
                logging.info(
                    f"[Sent #{message_count}] "
                    f"{reading['customer_id']}  HR={reading['heart_rate']:>3}"
                    f"  @ {reading['timestamp']}{flag}"
                )

            producer.flush()
            time.sleep(SEND_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logging.info(f"[Producer] Stopped. Total messages sent: {message_count}")
    finally:
        producer.flush()


if __name__ == "__main__":
    run_producer()
