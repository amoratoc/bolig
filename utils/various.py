import hashlib
from math import radians, sin, cos, sqrt, atan2


def hash_str(string: str):
    return hashlib.sha1(string.encode("utf-8")).hexdigest()


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth specified in decimal degrees.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius of the earth in kilometers. Use 3956 for miles
    return (r * c)/1000 # return in m


def find_nearest_stations(coords, stations):
    """
    Find the nearest Metrostation and S-station to the specified coordinates.
    """
    min_distance_metro = float('inf')
    nearest_metrostation = None

    min_distance_s_station = float('inf')
    nearest_s_station = None

    for station in stations:
        station_coords = station["coords"]
        distance = haversine_distance(coords[0], coords[1], station_coords["lat"], station_coords["lon"])

        if station["type"] == "Metrostation" and distance < min_distance_metro:
            min_distance_metro = distance
            nearest_metrostation = station

        if station["type"] == "S-station" and distance < min_distance_s_station:
            min_distance_s_station = distance
            nearest_s_station = station

    return nearest_metrostation, min_distance_metro, nearest_s_station, min_distance_s_station