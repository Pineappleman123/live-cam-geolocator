# Author: Andrew Perevoztchikov

# For scraping live security cam websites for footage
from bs4 import BeautifulSoup
import requests
# Using Nominatim to convert address that user provides to coords for simplicity
from geopy.geocoders import Nominatim
# Calculating distances
import math

def geocode(address):
    geolocator = Nominatim(user_agent="caltrans_cam_finder")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.
    """
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in kilometers

def extract_current_images(camera_data_list):
    current_images = []

    for camera in camera_data_list:
        # Drill down into the nested structure
        image_data = camera.get('imageData', {})
        current_url = image_data.get('static', {}).get('currentImageURL')

        if current_url:
            current_images.append({
                'location': camera.get('location', {}).get('locationName', 'Unknown'),
                'route': camera.get('location', {}).get('route', 'Unknown'),
                'direction': camera.get('location', {}).get('direction', 'Unknown'),
                'currentImageURL': current_url
            })

    return current_images

def get_closest_caltrans_cameras(user_lat, user_lon, top_n=5):
    """
    Fetches CCTV camera data from all Caltrans districts and returns the top_n closest cameras.
    """
    camera_list = []

    # Iterate through all 12 Caltrans districts
    for district in range(1, 13):
        try:
            lower = f"d{district}"
            upper = f"D{district:02}"
            base_url = f"https://cwwp2.dot.ca.gov/data/{lower}/cctv/cctvStatus{upper}.json"
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Adjust the parsing based on the actual JSON structure
            for cam in data.get("data", []):
                cctv = cam.get("cctv", {})
                location = cctv.get("location", {})
                image_data = cctv.get("imageData", {})
                lat = location.get("latitude")
                lon = location.get("longitude")
                image_url = image_data.get("static", {}).get("currentImageURL")
                if lat and lon and image_url:
                    distance = haversine(user_lat, user_lon, float(lat), float(lon))
                    camera_list.append({
                        "id": cctv.get("id", "Unknown ID"),
                        "description": location.get("locationName", "No Description"),
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": image_url,
                        "distance_km": distance
                    })
        except requests.RequestException as e:
            print(f"Error fetching data for district {district}: {e}")
            continue

    # Sort cameras by distance and return the top_n closest
    closest_cameras = sorted(camera_list, key=lambda x: x["distance_km"])[:top_n]
    return closest_cameras

# Example usage:
if __name__ == "__main__":
    user_latitude = 37.7749  # Example: San Francisco latitude
    user_longitude = -122.4194  # Example: San Francisco longitude
    closest_cams = get_closest_caltrans_cameras(user_latitude, user_longitude)
    for cam in closest_cams:
        print(f"{cam['id']} -- {cam['description']} ({cam['distance_km']:.2f} km): {cam['image_url']}")