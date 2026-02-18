# User Guide — Heartbeat Monitoring System

This guide walks you through setting up and running the Real-Time Customer Heartbeat Monitoring System. All commands use **rav** — a simple task runner. Run each command from the project root.

## Prerequisites

- **Docker Desktop** installed and running
- **Python 3.10+**
- **rav** installed (`pip install rav`)

---

## 1. Install Python Dependencies

```bash
rav run install
```

Installs `kafka-python-ng`, `pg8000`, and `faker` from `requirements.txt`.

---

## 2. Start Infrastructure

```bash
rav run up
```

Starts all Docker containers in the background:

| Container | Port | Purpose |
|-----------|------|---------|
| **Zookeeper** | 2181 | Kafka coordination |
| **Kafka** | 9092 | Message broker |
| **PostgreSQL** | 5432 | Data storage |
| **Grafana** | 3000 | Dashboard UI |

The database schema (`sql/schema.sql`) is automatically applied on first run.

### Check container status

```bash
rav run ps
```

### View live container logs

```bash
rav run logs
```

Press `Ctrl+C` to stop watching logs.

---

## 3. Run the Data Pipeline

Open **two separate terminals**:

### Terminal 1 — Start the Producer

```bash
rav run producer
```

Generates synthetic heartbeat data for 5 simulated customers and sends it to Kafka every second. You will see output like:

```
[Producer] Connected to Kafka at localhost:9092
[Producer] Publishing to topic: heartbeat-readings
[Producer] Simulating 5 customers

  [Sent #1] CUST-001  HR= 72  @ 2026-02-18T09:00:00
  [Sent #2] CUST-002  HR=145  @ 2026-02-18T09:00:00 ⚠ ANOMALY
```

### Terminal 2 — Start the Consumer

```bash
rav run consumer
```

Reads messages from Kafka, validates them, flags anomalies, and stores readings in PostgreSQL:

```
[Consumer] Listening on topic: heartbeat-readings
[Consumer] Connected to Kafka at localhost:9092

  [Stored #1] CUST-001  HR= 72  @ 2026-02-18T09:00:00
  [Stored #2] CUST-002  HR=145  @ 2026-02-18T09:00:00 ⚠ ANOMALY
```

Press `Ctrl+C` in each terminal to stop.

---

## 4. Open the Grafana Dashboard

```bash
rav run grafana
```

This prints the dashboard URL. Open it in your browser:

**http://localhost:3000/d/heartbeat-monitor**

- No login required (anonymous access is enabled)
- The dashboard auto-refreshes every **5 seconds**
- Three panels are available:
  - **Customer Statistics** — per-customer totals, averages, and anomaly counts
  - **Heart Rate Over Time** — live time-series chart with threshold markers
  - **Recent Anomalies** — table of flagged readings

---

## 5. Run Tests

### Full pipeline tests

```bash
rav run test
```

Runs component tests (data generator, DB connection, insert/query) from `tests/test_pipeline.py`.

### Database connection test

```bash
rav run db-test
```

Quick standalone test to verify PostgreSQL connectivity.

---

## 6. Stop the System

### Stop containers (keep data)

```bash
rav run down
```

### Stop containers and delete all data

```bash
rav run reset
```

This removes the PostgreSQL and Grafana data volumes — the database will be recreated fresh on the next `rav run up`.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `rav run install` | Install Python dependencies |
| `rav run up` | Start all Docker containers |
| `rav run down` | Stop all Docker containers |
| `rav run reset` | Stop containers and delete data volumes |
| `rav run logs` | Stream live container logs |
| `rav run ps` | Show container status |
| `rav run producer` | Start the Kafka producer |
| `rav run consumer` | Start the Kafka consumer |
| `rav run test` | Run pipeline tests |
| `rav run db-test` | Test database connection |
| `rav run grafana` | Show Grafana dashboard URL |
