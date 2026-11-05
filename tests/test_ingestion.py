
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ingest_tickets import upload_tickets


def test_duplicate_ticket_ids():
    """Check duplicate IDs are rejected."""

    df = pd.DataFrame({
        "ticket_id": [1, 1],
        "customer": ["Test A", "Test B"],
        "product": ["Dahua NVR", "Ajax Alarm"],
        "description": ["Offline", "Disconnected"],
        "priority": ["High", "Low"],
        "status": ["Open", "Closed"],
        "created_at": ["2026-11-01", "2026-11-02"]
    })

    with pytest.raises(ValueError, match="Duplicate"):
        upload_tickets(df, None)


def test_missing_ticket_ids():
    """Check missing IDs are rejected."""

    df = pd.DataFrame({
        "ticket_id": [1, None],
        "customer": ["Test A", "Test B"],
        "product": ["Dahua NVR", "Ajax Alarm"],
        "description": ["Offline", "Disconnected"],
        "priority": ["High", "Low"],
        "status": ["Open", "Closed"],
        "created_at": ["2026-11-01", "2026-11-02"]
    })

    with pytest.raises(ValueError, match="Missing"):
        upload_tickets(df, None)


def test_invalid_date():
    """Check invalid dates are rejected."""

    df = pd.DataFrame({
        "ticket_id": [1],
        "customer": ["Test A"],
        "product": ["Dahua NVR"],
        "description": ["Offline"],
        "priority": ["High"],
        "status": ["Open"],
        "created_at": ["not-a-date"]
    })

    with pytest.raises(ValueError):
        upload_tickets(df, None)
