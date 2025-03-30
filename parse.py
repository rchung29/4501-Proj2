import json
import pandas as pd

def parse_geo_string(geo_str):
    """Convert 'geo:lat,lon' -> (lat, lon) floats."""
    if not geo_str or not geo_str.startswith("geo:"):
        return None
    coords = geo_str.replace("geo:", "").split(",")
    if len(coords) != 2:
        return None
    try:
        lat = float(coords[0].strip())
        lon = float(coords[1].strip())
        return (lat, lon)
    except ValueError:
        return None

def parse_location_history(json_path):
    """
    Reads location-history JSON and returns a DataFrame,
    filtering out movement-based 'activity' entries so we only keep 'visit' points
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for entry in data:
        start_time = entry.get("startTime")
        end_time   = entry.get("endTime")

        if "visit" in entry and "topCandidate" in entry["visit"]:
            loc_str = entry["visit"]["topCandidate"].get("placeLocation")
            coords = parse_geo_string(loc_str)
            if coords:
                lat, lon = coords
                records.append({
                    "startTime": start_time,
                    "endTime": end_time,
                    "sourceType": "visit",
                    "latitude": lat,
                    "longitude": lon
                })

        if "activity" in entry:
            activity_type = entry["activity"].get("topCandidate", {}).get("type")

            start_coord = parse_geo_string(entry["activity"].get("start"))
            if start_coord:
                lat, lon = start_coord
                records.append({
                    "startTime": start_time,
                    "endTime": end_time,
                    "sourceType": "activityStart",
                    "activityType": activity_type,
                    "latitude": lat,
                    "longitude": lon
                })

            end_coord = parse_geo_string(entry["activity"].get("end"))
            if end_coord:
                lat, lon = end_coord
                records.append({
                    "startTime": start_time,
                    "endTime": end_time,
                    "sourceType": "activityEnd",
                    "activityType": activity_type,
                    "latitude": lat,
                    "longitude": lon
                })

    df = pd.DataFrame(records)

    df = df[
      (df["sourceType"] == "visit") |
      (df["activityType"].isin(["walking", "running"]))
    ].copy()

    return df
