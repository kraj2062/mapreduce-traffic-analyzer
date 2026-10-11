
import os
import sqlite3
import pandas as pd

DB_PATH = os.getenv("DB_PATH", "traffic.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_records (
                record_id INTEGER PRIMARY KEY,
                location TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                vehicle_count INTEGER NOT NULL,
                avg_speed REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                hour TEXT NOT NULL,
                total_vehicles INTEGER NOT NULL,
                average_speed REAL NOT NULL,
                congestion_score REAL NOT NULL,
                record_count INTEGER NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_size INTEGER,
                processing_time REAL,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_traffic_records(records):
    with get_connection() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO traffic_records
            (record_id, location, timestamp,
             vehicle_count, avg_speed)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                r["record_id"], r["location"], r["timestamp"],
                r["vehicle_count"], r["avg_speed"]
            )
            for r in records
        ])


def load_traffic_records():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM traffic_records", conn
        )


def save_analysis_results(results):
    with get_connection() as conn:
        conn.execute("DELETE FROM analysis_results")

        results.to_sql(
            "analysis_results",
            conn,
            if_exists="append",
            index=False
        )


def record_analysis_run(size, elapsed, status):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analysis_runs
            (dataset_size, processing_time, status)
            VALUES (?, ?, ?)
        """, (size, elapsed, status))
