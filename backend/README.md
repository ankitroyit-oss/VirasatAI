# VirasatAI Spatial REST Backend 🏛️⚡

Production-grade, asynchronous REST backend for live monument exploration, geospatial intelligence, and augmented reality (AR) tourism.

Built with **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0 (asyncio)**, **GeoAlchemy2**, and **PostgreSQL with PostGIS**.

---

## 🌟 Key Features

1. **⚡ Asynchronous High-Throughput Engine**:
   - Built on FastAPI and ASGI with `asyncpg` connection pooling.
   - Non-blocking I/O handling thousands of concurrent tourist geolocation requests.

2. **🛰️ PostGIS Spatial Indexing (`SRID 4326`)**:
   - Every monument stores a true PostGIS `Geometry(Point, 4326)` column with spatial GiST indexing.
   - Microsecond radius searches via `ST_DWithin` and sub-meter geodesic distance queries via `ST_Distance` on WGS 84 ellipsoids.

3. **📍 Real-Time Proximity Alert Engine**:
   - `/api/v1/spatial/proximity-detect` evaluates streaming GPS coordinates (`latitude`, `longitude`, `speed_mps`, `heading_deg`).
   - Dynamic 3-tier notification system:
     - 🔴 **In-Range Alert** (`< 500m`): Instant notification prompting AR camera activation.
     - 🟡 **Approaching Warning** (`< 2km`): Proximity alert with relative cardinal direction (`↑ Straight Ahead`, `↗ Slight Right`, etc.).
     - 🔵 **Nearby Discovery** (`< 10km`): Background awareness with estimated time of arrival (ETA).

4. **📱 AR Camera Telemetry & Occlusion Analysis**:
   - `/api/v1/ar/telemetry` combines observer coordinates, device compass heading (0–360°), and camera horizontal Field-of-View (FOV).
   - Computes angular displacement (`relative_bearing`) and determines whether the monument is within the camera viewfinder frame.
   - Emits real-time AR HUD guidance arrows (`🎯`, `↑`, `↗`, `→`, `↘`, `↓`, `↙`, `←`, `↖`).

5. **⭐ Visitor Reviews & 1–5 Star Aggregation**:
   - Full review lifecycle with real-time SQL aggregation of averages, totals, and star distributions.

6. **🗺️ RFC 7946 GeoJSON FeatureCollections**:
   - Direct compatibility with Mapbox GL, Leaflet, Google Maps, or custom SVG overlays.

7. **🌱 Automated 35-Monument Seeder**:
   - Automatically bootstraps all 35 verified Indian heritage sites (Taj Mahal, Konark, Hampi, Ajanta, etc.) into PostGIS spatial tables on startup.

---

## 🏗️ Architecture & Tech Stack

```
                               ┌────────────────────────────────┐
                               │   Mobile / Web AR Client       │
                               │   (Leaflet / Camera / GPS)     │
                               └───────────────┬────────────────┘
                                               │ HTTP / REST
                                               ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ FastAPI ASGI Application (Python 3.11+)                                       │
│                                                                               │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────┐  │
│  │   /api/v1/spatial     │  │     /api/v1/ar        │  │ /api/v1/monuments │  │
│  │ (Nearby & Proximity)  │  │ (Camera FOV & Vectors)│  │ (CRUD & Filtering)│  │
│  └───────────┬───────────┘  └───────────┬───────────┘  └─────────┬─────────┘  │
│              └──────────────────┐       │       ┌────────────────┘            │
│                                 ▼       ▼       ▼                             │
│                     ┌───────────────────────────────────────┐                 │
│                     │ SQLAlchemy 2.0 (Async Session)        │                 │
│                     │ GeoAlchemy2 Spatial Extensions        │                 │
│                     └───────────────────┬───────────────────┘                 │
└─────────────────────────────────────────┼─────────────────────────────────────┘
                                          │ asyncpg connection pool
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ PostgreSQL 16 + PostGIS 3.4           │
                      │ - Spatial GiST Index on POINT(4326)   │
                      │ - ST_DWithin, ST_Distance, ST_Azimuth │
                      └───────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
backend/
├── Dockerfile                   # Multi-stage Python 3.11 container with Geos & Proj libraries
├── docker-compose.yml           # Multi-container orchestration (PostGIS 16 + Backend)
├── requirements.txt             # Pinned async dependencies
├── .env.example                 # Environment configuration template
├── README.md                    # Backend documentation
└── app/
    ├── main.py                  # FastAPI app factory, CORS, lifespan startup
    ├── core/
    │   ├── config.py            # Pydantic v2 BaseSettings
    │   └── database.py          # Async engine, sessionmaker, Base model
    ├── models/
    │   ├── monument.py          # PostGIS Point Geometry model & JSONB columns
    │   └── review.py            # Foreign-key review model
    ├── schemas/
    │   ├── monument.py          # Monument validation & GeoJSON schemas
    │   ├── review.py            # Review & rating aggregation schemas
    │   └── spatial.py           # Proximity query & AR telemetry schemas
    ├── crud/
    │   ├── crud_monument.py     # PostGIS ST_DWithin & Haversine fallback
    │   └── crud_review.py       # SQL aggregate calculations
    ├── db/
    │   ├── init_db.py           # Table creation & seeder entrypoint
    │   ├── seed_data.py         # Seed loader helper
    │   └── seed_monuments.json  # 35 verified heritage sites dataset
    └── api/
        └── v1/
            ├── api.py           # Main v1 router aggregation
            └── endpoints/
                ├── health.py    # Health & PostGIS extension status
                ├── monuments.py # List, filter, CRUD monuments
                ├── spatial.py   # Nearby search, proximity alerts, GeoJSON
                ├── ar.py        # AR camera vector telemetry
                └── reviews.py   # Visitor reviews & ratings
```

---

## 🚀 Quickstart with Docker Compose

The fastest way to spin up the complete stack (PostgreSQL + PostGIS + FastAPI):

```bash
cd backend

# 1. Copy environment template
cp .env.example .env

# 2. Start PostGIS and FastAPI containers
docker compose up --build
```

- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.11 or higher
- PostgreSQL with PostGIS extension (`postgis/postgis` or `brew install postgis`)
- GDAL / GEOS development libraries (macOS: `brew install gdal geos proj`)

### 2. Virtual Environment & Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Ensure PostgreSQL is running and create the database:
```sql
CREATE DATABASE virasatai;
\c virasatai
CREATE EXTENSION postgis;
```

Configure `.env`:
```ini
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=virasatai
```

### 4. Run Initial Database Seeding

```bash
python -m app.db.init_db
```

### 5. Launch FastAPI Dev Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 Key API Endpoints & Usage

### 1. Spatial Nearby Search
Find monuments within a radius of user coordinates with exact distance and directional bearing:

```http
GET /api/v1/spatial/nearby?latitude=27.1751&longitude=78.0421&radius_meters=50000&limit=5
```

**Response**:
```json
[
  {
    "id": "taj-mahal",
    "name": "Taj Mahal",
    "name_hindi": "ताज महल",
    "emoji": "🕌",
    "image": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&q=80",
    "city": "Agra",
    "state": "Uttar Pradesh",
    "latitude": 27.1751,
    "longitude": 78.0421,
    "distance_meters": 0.0,
    "distance_km": 0.0,
    "bearing_degrees": 0.0,
    "relative_direction": "↑ Straight Ahead"
  },
  {
    "id": "agra-fort",
    "name": "Agra Fort",
    "name_hindi": "आगरा का किला",
    "emoji": "🏰",
    "image": "https://images.unsplash.com/photo-1585136917228-569b7b752251?w=800&q=80",
    "city": "Agra",
    "state": "Uttar Pradesh",
    "latitude": 27.1795,
    "longitude": 78.0211,
    "distance_meters": 2134.8,
    "distance_km": 2.13,
    "bearing_degrees": 283.4,
    "relative_direction": "← Turn Left"
  }
]
```

---

### 2. Live Dynamic Proximity Alert Engine
Continuously streams user coordinates and speed to generate tiered alerts for mobile apps:

```http
POST /api/v1/spatial/proximity-detect
Content-Type: application/json

{
  "latitude": 27.1760,
  "longitude": 78.0410,
  "accuracy_meters": 5.0,
  "speed_mps": 1.4,
  "heading_deg": 45.0
}
```

**Response**:
```json
{
  "user_latitude": 27.176,
  "user_longitude": 78.041,
  "speed_kmh": 5.0,
  "has_active_alerts": true,
  "alerts": [
    {
      "monument_id": "taj-mahal",
      "name": "Taj Mahal",
      "tier": "alert",
      "distance_meters": 147.2,
      "distance_formatted": "147 m",
      "bearing_degrees": 137.5,
      "relative_direction": "→ Turn Right",
      "eta_seconds": 105,
      "notification_title": "Monument in Range: Taj Mahal",
      "notification_body": "You are within 147 meters of Taj Mahal! Point your camera to explore in AR."
    }
  ]
}
```

---

### 3. AR Camera Vector Telemetry
Provides real-time camera viewfinder alignment data:

```http
POST /api/v1/ar/telemetry
Content-Type: application/json

{
  "user_latitude": 27.1760,
  "user_longitude": 78.0410,
  "device_heading": 135.0,
  "camera_fov_horizontal": 65.0,
  "target_monument_id": "taj-mahal"
}
```

**Response**:
```json
{
  "target_id": "taj-mahal",
  "target_name": "Taj Mahal",
  "target_latitude": 27.1751,
  "target_longitude": 78.0421,
  "distance_meters": 147.2,
  "distance_formatted": "147 m",
  "bearing_degrees": 137.5,
  "relative_bearing": 2.5,
  "is_in_camera_fov": true,
  "direction_arrow": "🎯",
  "direction_label": "In Viewfinder (2° offset)"
}
```

---

### 4. Visitor Reviews & Star Ratings

#### Submit Review:
```http
POST /api/v1/monuments/taj-mahal/reviews
Content-Type: application/json

{
  "author": "Priya Sharma",
  "rating": 5,
  "text": "Breathtaking morning view. The AR insights made the history come alive!",
  "visit_date": "October 2024"
}
```

#### Get Aggregated Ratings:
```http
GET /api/v1/monuments/taj-mahal/ratings
```

**Response**:
```json
{
  "average": 4.9,
  "total": 48,
  "distribution": {
    "1": 0,
    "2": 0,
    "3": 1,
    "4": 3,
    "5": 44
  }
}
```

---

### 5. RFC 7946 GeoJSON FeatureCollection

```http
GET /api/v1/spatial/geojson?category=temple
```

Returns standard GeoJSON with Point geometries `[longitude, latitude]` for mapping engines.

---

## ⚡ PostGIS Performance Optimization Details

1. **Spatial GiST Indexing**:
   ```sql
   CREATE INDEX idx_monuments_geom ON monuments USING GIST (geom);
   ```
2. **True Geodesic Distance via PostGIS Geography**:
   ```sql
   SELECT id, name,
          ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(78.0421, 27.1751), 4326)::geography) AS distance_m
   FROM monuments
   WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(78.0421, 27.1751), 4326)::geography, 50000)
   ORDER BY distance_m ASC
   LIMIT 10;
   ```
3. **Ellipsoidal Forward Bearing**:
   ```sql
   SELECT degrees(ST_Azimuth(
       ST_SetSRID(ST_MakePoint(78.0421, 27.1751), 4326),
       geom
   )) AS bearing_deg;
   ```

---

## 🛡️ License

MIT License. Developed for VirasatAI Heritage & Cultural Tourism Platform.
