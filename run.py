from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# OSM Nominatim POI / 地名搜索接口
@app.route("/api/search")
def search_poi():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 10
    }
    headers = {
        "User-Agent": "MapBrowserApp/1.0 (Contact: local@mapping.tool)"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=6)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Overpass API 范围 POI 查询接口
@app.route("/api/pois")
def get_pois_in_bbox():
    # 接收当前地图视窗边界: south, west, north, east
    try:
        s = float(request.args.get("s"))
        w = float(request.args.get("w"))
        n = float(request.args.get("n"))
        e = float(request.args.get("e"))
    except (TypeError, ValueError):
        return jsonify([])

    # Overpass QL: 查询视窗内常见的节点 POI (餐饮、旅游、便民、商户)
    overpass_query = f"""
    [out:json][timeout:15];
    (
      node["amenity"]({s},{w},{n},{e});
      node["tourism"]({s},{w},{n},{e});
      node["shop"]({s},{w},{n},{e});
    );
    out body 80;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        resp = requests.post(url, data=overpass_query, timeout=10)
        data = resp.json()
        
        pois = []
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            name = tags.get("name") or tags.get("name:en") or tags.get("amenity") or tags.get("shop") or "未知设施"
            category = tags.get("amenity") or tags.get("tourism") or tags.get("shop") or "POI"
            pois.append({
                "id": elem.get("id"),
                "lat": elem.get("lat"),
                "lon": elem.get("lon"),
                "name": name,
                "category": category
            })
        return jsonify(pois)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Google 卫星 + WGS84 原生 POI 系统</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; height: 100vh; background: #1a1a1a; color: #fff; }
            
            .header-bar {
                height: 56px;
                padding: 0 16px;
                display: flex;
                align-items: center;
                gap: 16px;
                background: #242424;
                border-bottom: 1px solid #333;
                z-index: 1000;
            }
            .header-bar h1 { font-size: 16px; font-weight: 600; }
            
            .search-box {
                position: relative;
                display: flex;
                align-items: center;
            }
            .search-box input {
                width: 320px;
                height: 36px;
                padding: 0 12px;
                border-radius: 4px 0 0 4px;
                border: 1px solid #444;
                background: #181818;
                color: #fff;
                font-size: 14px;
            }
            .search-box button {
                height: 36px;
                padding: 0 16px;
                border: none;
                background: #2563eb;
                color: white;
                font-weight: 500;
                cursor: pointer;
                border-radius: 0 4px 4px 0;
            }
            .search-box button:hover { background: #1d4ed8; }
            
            .results-list {
                position: absolute;
                top: 40px;
                left: 0;
                width: 100%;
                background: #222;
                border: 1px solid #444;
                border-radius: 4px;
                list-style: none;
                max-height: 280px;
                overflow-y: auto;
                display: none;
                box-shadow: 0 8px 16px rgba(0,0,0,0.5);
            }
            .results-list li {
                padding: 10px 12px;
                font-size: 13px;
                border-bottom: 1px solid #333;
                cursor: pointer;
            }
            .results-list li:hover { background: #333; }
            
            .toggle-btn {
                background: #374151;
                border: none;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
            }
            .toggle-btn.active { background: #10b981; }

            #map { flex: 1; width: 100%; }
        </style>
    </head>
    <body>
        <div class="header-bar">
            <h1>🌍 卫星地图 POI 系统</h1>
            
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="搜索全球地点 / POI (Nominatim)..." onkeydown="if(event.key==='Enter') doSearch()" />
                <button onclick="doSearch()">搜索</button>
                <ul id="searchResults" class="results-list"></ul>
            </div>

            <button id="togglePoiBtn" class="toggle-btn active" onclick="toggleDynamicPoi()">视窗 POI 探索: 开启</button>
        </div>

        <div id="map"></div>

        <script>
            // 初始化地图 (WGS-84 原生坐标)
            const map = L.map('map', { maxZoom: 20 }).setView([39.9042, 116.4074], 15);

            // 1. 底图：Google 卫星 (WGS-84)
            const googleSat = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
                maxZoom: 20,
                attribution: 'Google Satellite'
            }).addTo(map);

            // 2. WGS-84 透明路网与注记层
            const cartoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png', {
                subdomains: 'abcd',
                maxZoom: 20,
                attribution: '&copy; OpenStreetMap'
            }).addTo(map);

            // 图层组
            const searchLayer = L.layerGroup().addTo(map);
            const dynamicPoiLayer = L.layerGroup().addTo(map);

            L.control.layers({
                "Google 卫星": googleSat
            }, {
                "WGS-84 透明路网": cartoLabels,
                "搜索定位标记": searchLayer,
                "视窗动态 POI": dynamicPoiLayer
            }).addTo(map);

            // 搜索功能 (Nominatim API)
            async function doSearch() {
                const query = document.getElementById('searchInput').value;
                const resultsUl = document.getElementById('searchResults');
                if (!query) return;

                resultsUl.style.display = 'block';
                resultsUl.innerHTML = '<li style="color:#aaa;">正在检索...</li>';

                try {
                    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    
                    resultsUl.innerHTML = '';
                    if (!data.length) {
                        resultsUl.innerHTML = '<li style="color:#aaa;">未找到相关结果</li>';
                        return;
                    }

                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item.display_name;
                        li.onclick = () => {
                            const lat = parseFloat(item.lat);
                            const lon = parseFloat(item.lon);
                            map.flyTo([lat, lon], 16);
                            searchLayer.clearLayers();
                            L.marker([lat, lon])
                             .addTo(searchLayer)
                             .bindPopup(`<b>${item.display_name}</b><br>坐标: [${lat.toFixed(5)}, ${lon.toFixed(5)}]`)
                             .openPopup();
                            resultsUl.style.display = 'none';
                        };
                        resultsUl.appendChild(li);
                    });
                } catch (e) {
                    resultsUl.innerHTML = '<li style="color:#f87171;">检索失败，请重试</li>';
                }
            }

            // 动态视窗 POI 加载 (Overpass API)
            let poiEnabled = true;
            let debounceTimer = null;

            function toggleDynamicPoi() {
                poiEnabled = !poiEnabled;
                const btn = document.getElementById('togglePoiBtn');
                if (poiEnabled) {
                    btn.classList.add('active');
                    btn.textContent = '视窗 POI 探索: 开启';
                    fetchPois();
                } else {
                    btn.classList.remove('active');
                    btn.textContent = '视窗 POI 探索: 关闭';
                    dynamicPoiLayer.clearLayers();
                }
            }

            async function fetchPois() {
                if (!poiEnabled || map.getZoom() < 14) {
                    if (map.getZoom() < 14) dynamicPoiLayer.clearLayers();
                    return;
                }

                const b = map.getBounds();
                const url = `/api/pois?s=${b.getSouth()}&w=${b.getWest()}&n=${b.getNorth()}&e=${b.getEast()}`;

                try {
                    const res = await fetch(url);
                    const pois = await res.json();
                    
                    dynamicPoiLayer.clearLayers();
                    pois.forEach(p => {
                        L.circleMarker([p.lat, p.lon], {
                            radius: 5,
                            color: '#38bdf8',
                            fillColor: '#0284c7',
                            fillOpacity: 0.8,
                            weight: 2
                        })
                        .bindPopup(`<b>${p.name}</b><br>类别: ${p.category}<br>WGS84: ${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`)
                        .addTo(dynamicPoiLayer);
                    });
                } catch (e) {
                    console.error("加载视窗 POI 失败", e);
                }
            }

            // 监听地图移动与缩放事件
            map.on('moveend', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(fetchPois, 500);
            });

            // 首次加载
            fetchPois();

            // 点击其他区域隐藏搜索建议下拉框
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-box')) {
                    document.getElementById('searchResults').style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=1989, debug=True)