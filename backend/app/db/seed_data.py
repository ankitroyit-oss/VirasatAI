"""Seed dataset for initial PostGIS migration."""

import json
from pathlib import Path
from typing import Any, Dict, List

SEED_FILE = Path(__file__).parent / "seed_monuments.json"


def get_seed_monuments() -> List[Dict[str, Any]]:
    """Load verified monument records from seed_monuments.json."""
    if SEED_FILE.exists():
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Initial sample reviews to seed
SAMPLE_REVIEWS = [
    {
        "monument_id": "taj-mahal",
        "author": "Aarav Sharma",
        "rating": 5,
        "text": "Breathtaking monument at sunrise! The white marble reflects golden hues. Truly an architectural marvel.",
        "visit_date": "October 2025"
    },
    {
        "monument_id": "taj-mahal",
        "author": "Meera Sen",
        "rating": 5,
        "text": "The symmetry and intricate pietra dura inlay work is world-class. Worth every minute.",
        "visit_date": "December 2025"
    },
    {
        "monument_id": "red-fort",
        "author": "Vikram Malhotra",
        "rating": 5,
        "text": "Massive red sandstone ramparts. Standing where the national flag is unfurled was an emotional experience.",
        "visit_date": "January 2026"
    },
    {
        "monument_id": "hampi",
        "author": "Rohit Verma",
        "rating": 5,
        "text": "Surreal boulder landscapes and stone chariot at Vijaya Vittala temple. Rent a cycle to explore!",
        "visit_date": "November 2025"
    },
    {
        "monument_id": "konark-sun-temple",
        "author": "Priya Das",
        "rating": 5,
        "text": "The giant carved chariot wheels acting as sundials are an astronomical and artistic masterpiece.",
        "visit_date": "February 2026"
    }
]
