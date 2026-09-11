"""Backend Unit and Integration Tests."""

import math
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.crud.crud_monument import CRUDMonument
from app.db.seed_data import get_seed_monuments, SAMPLE_REVIEWS
from app.schemas.spatial import (
    ARVectorTelemetryRequest,
    ProximityAlertRequest,
    NearbyMonumentResult
)

client = TestClient(app)


def test_root_endpoint():
    """Verify root API ping returns 200 OK and endpoint catalog."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "VirasatAI" in data["service"]
    assert data["documentation"]["swagger_ui"] == "/docs"
    assert "endpoints" in data


def test_openapi_json_schema():
    """Verify OpenAPI 3.1.0 schema is generated correctly."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "VirasatAI Spatial Engine"
    assert "/api/v1/spatial/nearby" in schema["paths"]
    assert "/api/v1/ar/telemetry" in schema["paths"]
    assert "/api/v1/monuments/" in schema["paths"]


def test_spatial_haversine_distance():
    """Test Haversine distance accuracy."""
    # Taj Mahal (27.1751, 78.0421) to Agra Fort (27.1795, 78.0211) is ~2.13 km
    dist = CRUDMonument.haversine_distance(27.1751, 78.0421, 27.1795, 78.0211)
    assert 2000 < dist < 2300, f"Unexpected distance: {dist}"

    # Self distance is 0.0
    self_dist = CRUDMonument.haversine_distance(27.1751, 78.0421, 27.1751, 78.0421)
    assert self_dist == 0.0


def test_spatial_forward_azimuth():
    """Test forward bearing angle calculation."""
    # Due North: lat increases, lon constant
    bearing_north = CRUDMonument.forward_azimuth(10.0, 70.0, 20.0, 70.0)
    assert abs(bearing_north - 0.0) < 0.1 or abs(bearing_north - 360.0) < 0.1

    # Due East: lat constant, lon increases
    bearing_east = CRUDMonument.forward_azimuth(10.0, 70.0, 10.0, 80.0)
    assert abs(bearing_east - 90.0) < 1.0


def test_relative_direction_derivation():
    """Test cardinal direction mapping based on bearing and heading."""
    # Directly ahead (bearing 90, heading 90 -> diff 0)
    assert CRUDMonument.calculate_relative_direction(90.0, 90.0) == "↑ Straight Ahead"

    # Turn right (bearing 180, heading 90 -> diff 90)
    assert CRUDMonument.calculate_relative_direction(180.0, 90.0) == "→ Turn Right"

    # Turn left (bearing 0, heading 90 -> diff 270)
    assert CRUDMonument.calculate_relative_direction(0.0, 90.0) == "← Turn Left"

    # Behind you (bearing 270, heading 90 -> diff 180)
    assert CRUDMonument.calculate_relative_direction(270.0, 90.0) == "↓ Behind You"


def test_seed_monuments_integrity():
    """Verify seed monuments dataset contains all 35 sites with verified attributes."""
    monuments = get_seed_monuments()
    assert len(monuments) >= 35, f"Expected 35 monuments, got {len(monuments)}"

    ids = set()
    for m in monuments:
        assert m["id"] not in ids, f"Duplicate ID found: {m['id']}"
        ids.add(m["id"])
        assert "name" in m and len(m["name"]) > 0
        assert "city" in m and len(m["city"]) > 0
        assert "state" in m and len(m["state"]) > 0
        assert "latitude" in m and -90 <= m["latitude"] <= 90
        assert "longitude" in m and -180 <= m["longitude"] <= 180
        assert "category" in m


def test_seed_reviews_integrity():
    """Verify sample reviews data structure."""
    assert len(SAMPLE_REVIEWS) > 0
    for rev in SAMPLE_REVIEWS:
        assert "monument_id" in rev
        assert "author" in rev
        assert 1 <= rev["rating"] <= 5
