# Caltrans CCTV Camera Scraper and Visualizer

This Python utility fetches and visualizes traffic camera data from Caltrans (California Department of Transportation) CCTV feeds. It allows users to enter a physical address or GPS coordinates, then automatically locates and displays images from the nearest live traffic cameras in a collage format.

---

## Features

- Geolocation-based camera lookup via address or GPS coordinates
- Uses Caltrans CCTV JSON across all 12 California districts to lookup cameras

---

## Installation

Before running the script, ensure that the required dependencies are installed. You can install them using `pip`:

```bash
pip install requests pillow geopy
