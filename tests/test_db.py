"""Unit tests for src/db.py — all database interactions are mocked."""

from unittest.mock import MagicMock, patch

import pytest

import db


@pytest.fixture
def mock_db():
    """Patch db.get_connection so it returns a mock connection and cursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    with patch("db.get_connection", return_value=mock_conn):
        yield mock_conn, mock_cursor


# ── get_connection ───────────────────────────────────────────────


@patch("db.pg8000.dbapi.connect")
@patch("db.DB_CONFIG", {"host": "localhost", "port": 5432, "database": "test"})
def test_get_connection_calls_pg8000(mock_connect):
    db.get_connection()
    mock_connect.assert_called_once_with(host="localhost", port=5432, database="test")


# ── insert_reading ───────────────────────────────────────────────


def test_insert_reading_executes_sql(mock_db, sample_reading):
    mock_conn, mock_cursor = mock_db
    db.insert_reading(sample_reading)

    mock_cursor.execute.assert_called_once()
    sql_arg, params_arg = mock_cursor.execute.call_args[0]
    assert "INSERT INTO heartbeat_readings" in sql_arg
    assert params_arg == (
        sample_reading["customer_id"],
        sample_reading["heart_rate"],
        sample_reading["timestamp"],
        sample_reading["is_anomaly"],
    )


def test_insert_reading_commits(mock_db, sample_reading):
    mock_conn, mock_cursor = mock_db
    db.insert_reading(sample_reading)
    mock_conn.commit.assert_called_once()


# ── insert_readings_batch ────────────────────────────────────────


def test_insert_readings_batch_executemany(mock_db):
    mock_conn, mock_cursor = mock_db
    readings = [
        {
            "customer_id": "CUST-001",
            "heart_rate": 72,
            "timestamp": "2026-01-01T00:00:00+00:00",
            "is_anomaly": False,
        },
        {
            "customer_id": "CUST-002",
            "heart_rate": 185,
            "timestamp": "2026-01-01T00:00:01+00:00",
            "is_anomaly": True,
        },
    ]
    db.insert_readings_batch(readings)

    mock_cursor.executemany.assert_called_once()
    sql_arg, params_arg = mock_cursor.executemany.call_args[0]
    assert "INSERT INTO heartbeat_readings" in sql_arg
    assert params_arg == [
        ("CUST-001", 72, "2026-01-01T00:00:00+00:00", False),
        ("CUST-002", 185, "2026-01-01T00:00:01+00:00", True),
    ]


def test_insert_readings_batch_commits(mock_db, sample_reading):
    mock_conn, mock_cursor = mock_db
    db.insert_readings_batch([sample_reading])
    mock_conn.commit.assert_called_once()


# ── query_latest_readings ────────────────────────────────────────


def test_query_latest_readings_returns_results(mock_db):
    mock_conn, mock_cursor = mock_db
    expected = [("CUST-001", 72, "2026-01-01T00:00:00+00:00", False)]
    mock_cursor.fetchall.return_value = expected

    result = db.query_latest_readings()
    assert result == expected


def test_query_latest_readings_default_limit(mock_db):
    mock_conn, mock_cursor = mock_db
    db.query_latest_readings()

    sql_arg, params_arg = mock_cursor.execute.call_args[0]
    assert params_arg == (20,)


def test_query_latest_readings_custom_limit(mock_db):
    mock_conn, mock_cursor = mock_db
    db.query_latest_readings(limit=5)

    sql_arg, params_arg = mock_cursor.execute.call_args[0]
    assert params_arg == (5,)


# ── query_anomalies ──────────────────────────────────────────────


def test_query_anomalies_filters_anomalies(mock_db):
    mock_conn, mock_cursor = mock_db
    db.query_anomalies()

    sql_arg = mock_cursor.execute.call_args[0][0]
    assert "is_anomaly = TRUE" in sql_arg


# ── get_customer_stats ───────────────────────────────────────────


def test_get_customer_stats_returns_results(mock_db):
    mock_conn, mock_cursor = mock_db
    expected = [("CUST-001", 10, 72.0, 60, 90, 2)]
    mock_cursor.fetchall.return_value = expected

    result = db.get_customer_stats()
    assert result == expected


def test_get_customer_stats_groups_by_customer(mock_db):
    mock_conn, mock_cursor = mock_db
    db.get_customer_stats()

    sql_arg = mock_cursor.execute.call_args[0][0]
    assert "GROUP BY customer_id" in sql_arg
