# OpenStreetEarth
A project based on openstreetmap and google satelite image
# 🌍 OpenStreetEarth

`OpenStreetEarth` is a lightweight, high-precision map browser designed to bridge Google Satellite imagery with native WGS-84 coordinates and OpenStreetMap (OSM) POI data, completely bypassing GCJ-02 offsets in mainland China.

---

## ✨ Features

- **True WGS-84 Alignment**: Seamlessly integrates Google Satellite tiles with global standard WGS-84 coordinates without shifting.
- **Dynamic POI Exploration**: Real-time bounding box queries using the Overpass API for fast local exploration.
- **Global Search**: Powered by OSM Nominatim for accurate worldwide geocoding and location search.
- **Lightweight Stack**: Minimalist architecture built with Python Flask and Leaflet.js.

---

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourname/openstreetearth.git](https://github.com/yourname/openstreetearth.git)
   cd openstreetearth

```

2. **Install dependencies:**
```bash
pip install flask requests

```


3. **Run the application:**
```bash
python run.py

```


4. **Access the local server:**
Open your browser and navigate to: `http://127.0.0.1:1989`

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask, Requests
* **Frontend**: Leaflet.js, HTML5, CSS3
* **Data Sources**: Google Satellite Tiles, OpenStreetMap (Nominatim & Overpass API), CartoDB Basemaps

---

## 📄 License

This project is open-source under the [MIT License](https://www.google.com/search?q=LICENSE).

```

```
