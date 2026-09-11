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


def test_health_endpoint():
    """Verify health endpoint returns status healthy."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "latency_ms" in data


def test_list_monuments_endpoint():
    """Verify list monuments returns 35 verified heritage sites."""
    response = client.get("/api/v1/monuments/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 35
    assert any(m["id"] == "taj-mahal" for m in items)
    assert any(m["id"] == "red-fort" for m in items)


def test_get_categories_and_states():
    """Verify categories and states endpoints."""
    cats = client.get("/api/v1/monuments/categories").json()
    assert len(cats) >= 4
    states = client.get("/api/v1/monuments/states").json()
    assert len(states) >= 10


def test_get_monument_detail():
    """Verify detailed monument fetch."""
    res = client.get("/api/v1/monuments/taj-mahal")
    assert res.status_code == 200
    m = res.json()
    assert m["name"] == "Taj Mahal"
    assert m["unesco"] is True
    assert "architecture" in m
    assert "visit_info" in m


def test_spatial_nearby_endpoint():
    """Verify spatial nearby returns sites sorted by geodesic distance."""
    res = client.get("/api/v1/spatial/nearby?latitude=27.1751&longitude=78.0421&radius_meters=10000")
    assert res.status_code == 200
    nearby = res.json()
    assert len(nearby) > 0
    assert nearby[0]["id"] == "taj-mahal"
    assert nearby[0]["distance_meters"] < 10


def test_proximity_detect_endpoint():
    """Verify real-time proximity alert generation."""
    payload = {
        "latitude": 27.1760,
        "longitude": 78.0425,
        "heading_deg": 45.0,
        "speed_mps": 1.4
    }
    res = client.post("/api/v1/spatial/proximity-detect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_active_alerts"] is True
    assert len(data["alerts"]) > 0
    assert data["closest_monument"]["id"] == "taj-mahal"


def test_ar_telemetry_endpoint():
    """Verify AR camera vector telemetry."""
    payload = {
        "user_latitude": 27.1700,
        "user_longitude": 78.0400,
        "device_heading": 30.0,
        "camera_fov_horizontal": 65.0,
        "target_monument_id": "taj-mahal"
    }
    res = client.post("/api/v1/ar/telemetry", json=payload)
    assert res.status_code == 200
    telemetry = res.json()
    assert telemetry["target_id"] == "taj-mahal"
    assert "direction_arrow" in telemetry
    assert "distance_formatted" in telemetry


def test_geojson_endpoint():
    """Verify RFC 7946 GeoJSON FeatureCollection."""
    res = client.get("/api/v1/spatial/geojson")
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 35

