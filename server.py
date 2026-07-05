from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent
GOLD_DIR = ROOT_DIR / "lakehouse" / "gold" / "hourly_user_engagement"
SILVER_DIR = ROOT_DIR / "lakehouse" / "silver" / "clickstream_cleansed"
DLQ_DIR = ROOT_DIR / "lakehouse" / "bronze" / "dlq"

app = FastAPI(title="NexusFlow Lakehouse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read_duckdb_table(path: Path, table_name: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    pattern = str(path.resolve()).replace("\\", "/")
    if path.suffix == ".parquet":
        pattern = str(path.resolve()).replace("\\", "/")
    else:
        pattern = f"{pattern}/*.parquet"

    conn = duckdb.connect()
    try:
        result = conn.execute(f"SELECT * FROM read_parquet('{pattern}')").fetchdf()
        return result.to_dict(orient="records")
    finally:
        conn.close()


def _normalize_event_type(value: Any) -> str:
    if value is None:
        return "view"
    normalized = str(value).strip().lower().replace(" ", "_")
    aliases = {
        "view": "view",
        "views": "view",
        "click": "click",
        "clicks": "click",
        "add_to_cart": "add_to_cart",
        "add-to-cart": "add_to_cart",
        "purchase": "purchase",
        "purchases": "purchase",
    }
    return aliases.get(normalized, normalized)


def _to_display_name(event_type: str) -> str:
    labels = {
        "view": "Views",
        "click": "Clicks",
        "add_to_cart": "Add to Cart",
        "purchase": "Purchases",
    }
    return labels.get(event_type, event_type.replace("_", " ").title())


def _read_dlq_error_count() -> int:
    if not DLQ_DIR.exists():
        return 0

    count = 0
    for file_path in DLQ_DIR.rglob("*.json"):
        if not file_path.is_file():
            continue
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                count += len(payload)
            else:
                count += 1
        except Exception:
            count += 1
    return count


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
    gold_rows = _read_duckdb_table(GOLD_DIR, "gold_metrics")
    silver_rows = _read_duckdb_table(SILVER_DIR, "silver_events")

    telemetry: list[dict[str, Any]] = []
    category_map = {
        "view": {"name": "Views", "events": 0, "users": 0},
        "click": {"name": "Clicks", "events": 0, "users": 0},
        "add_to_cart": {"name": "Add to Cart", "events": 0, "users": 0},
        "purchase": {"name": "Purchases", "events": 0, "users": 0},
    }

    for row in gold_rows:
        event_type = _normalize_event_type(row.get("event_type") or row.get("eventType") or "view")
        if event_type not in category_map:
            continue

        total_events = row.get("total_events") or row.get("totalEvents") or 0
        unique_users = row.get("unique_users") or row.get("uniqueUsers") or 0
        category_map[event_type]["events"] += int(total_events or 0)
        category_map[event_type]["users"] += int(unique_users or 0)

    telemetry = [
        {"name": entry["name"], "events": entry["events"], "users": entry["users"]}
        for entry in category_map.values()
    ]

    total_events = sum(int(row.get("total_events") or row.get("totalEvents") or 0) for row in gold_rows)
    unique_users = max((int(row.get("unique_users") or row.get("uniqueUsers") or 0) for row in gold_rows), default=0)
    conversion_efficiency = round((total_events / max(total_events, 1)) * 100, 2) if total_events else 0.0
    dlq_error_count = _read_dlq_error_count()

    transactions: list[dict[str, Any]] = []
    for index, row in enumerate(silver_rows[:12]):
        event_type = _normalize_event_type(row.get("event_type") or row.get("eventType") or "view")
        timestamp = (
            row.get("timestamp")
            or row.get("event_timestamp")
            or row.get("eventTime")
            or row.get("ts")
            or ""
        )
        user_id = row.get("user_id") or row.get("userId") or row.get("user") or f"user-{index + 1}"
        transactions.append(
            {
                "id": f"txn-{index + 1:03d}",
                "eventType": event_type,
                "eventLabel": _to_display_name(event_type),
                "userId": str(user_id),
                "timestamp": str(timestamp),
                "status": "ingested",
            }
        )

    return {
        "summary": {
            "total_events": total_events,
            "unique_users": unique_users,
            "conversion_efficiency": conversion_efficiency,
            "dlq_error_count": dlq_error_count,
            "has_dlq_errors": dlq_error_count > 0,
        },
        "telemetry": telemetry,
        "transactions": transactions,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
