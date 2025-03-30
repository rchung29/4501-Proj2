import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.geocoders import Nominatim
from parse import parse_location_history

def main():
    df = parse_location_history("location-history.json")
    coords = df[['latitude', 'longitude']].values
    dbscan = DBSCAN(eps=0.00075, min_samples=5, metric='euclidean')
    cluster_labels = dbscan.fit_predict(coords)
    df['cluster_id'] = cluster_labels
    unique_clusters = [c for c in set(cluster_labels) if c != -1]
    geolocator = Nominatim(user_agent="my-app")

    for cluster_id in unique_clusters:
        cluster_points = df[df['cluster_id'] == cluster_id]
        representative_lat = cluster_points['latitude'].median()
        representative_lon = cluster_points['longitude'].median()
        location = geolocator.reverse((representative_lat, representative_lon))
        if location:
            osm_class = location.raw.get('class', '')
            osm_type = location.raw.get('type', '')
            place_name = f"{location.address} ({osm_class}:{osm_type})" if (osm_class or osm_type) else location.address
        else:
            place_name = None
        df.loc[df['cluster_id'] == cluster_id, 'place_name'] = place_name

    place_counts = df['place_name'].value_counts()
    print("Top 10 visited cluster addresses (with class:type):")
    print(place_counts.head(10))

if __name__ == "__main__":
    main()
