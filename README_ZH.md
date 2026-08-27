# 🌍 OpenStreetEarth

*[English README](README.md) | [简体中文说明](README_ZH.md)*

`OpenStreetEarth` 是一个轻量级、高精度的地图浏览器，旨在将 Google 卫星影像与标准的全球 WGS-84 坐标及 OpenStreetMap (OSM) POI 数据无缝结合，完美解决中国大陆地区的 GCJ-02（火星坐标系）偏移困扰。

---

## ✨ 功能特性

- **原生 WGS-84 对齐**：无缝整合 Google 卫星瓦片与全球标准 WGS-84 坐标，告别国内地图偏移。
- **视窗动态 POI 探索**：利用 Overpass API 实现地图视窗移动时的实时周边 POI 动态加载。
- **全球地名搜索**：基于 OSM Nominatim 提供精准的全球地理编码与位置检索。
- **极简技术栈**：采用 Python Flask 与 Leaflet.js 构建，轻量高效，开箱即用。

---

## 🚀 快速开始

1. **克隆仓库：**
   ```bash
   git clone [https://github.com/yourname/openstreetearth.git](https://github.com/yourname/openstreetearth.git)
   cd openstreetearth

```

2. **安装依赖：**

pip install flask requests

```


3. **运行程序：**
```bash
python run.py

```


4. **访问本地服务：**
打开浏览器并访问：`http://127.0.0.1:1989`

---

## 🛠️ 技术栈

* **后端**：Python, Flask, Requests
* **前端**：Leaflet.js, HTML5, CSS3
* **数据源**：Google 卫星瓦片、OpenStreetMap (Nominatim & Overpass API)、CartoDB 矢量路网/注记底图

---

## 📄 许可证

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 开源。
