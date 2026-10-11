
import pandas as pd
from collections import defaultdict


def map_traffic_records(df):
    
    mapped_data = []

    for _, row in df.iterrows():
        timestamp = pd.to_datetime(row["timestamp"])
        hour = timestamp.strftime("%Y-%m-%d %H:00")
        key = (str(row["location"]), hour)

        value = {
            "vehicle_count": int(row["vehicle_count"]),
            "speed": float(row["avg_speed"])
        }

        mapped_data.append((key, value))

    return mapped_data


def shuffle_and_group(mapped_data):
   
    grouped_data = defaultdict(list)

    for key, value in mapped_data:
        grouped_data[key].append(value)

    return grouped_data


def reduce_traffic_records(grouped_data):
   
    results = []

    for (location, hour), values in grouped_data.items():
        total_vehicles = sum(
            item["vehicle_count"] for item in values
        )

        average_speed = sum(
            item["speed"] for item in values
        ) / len(values)

        congestion_score = total_vehicles / max(average_speed, 1)

        results.append({
            "location": location,
            "hour": hour,
            "total_vehicles": total_vehicles,
            "average_speed": round(average_speed, 2),
            "congestion_score": round(congestion_score, 2),
            "record_count": len(values)
        })

    return pd.DataFrame(results)


def analyze_traffic(df):
   
    mapped = map_traffic_records(df)
    grouped = shuffle_and_group(mapped)
    results = reduce_traffic_records(grouped)

    return results
