from datetime import datetime
import json


from const import CONFIG_PATH


def parse_time(data):
    start_time_str = data['start']
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

    if data['duration'] < 0:
        now = datetime.now(start_time.tzinfo)
        duration_seconds = (now - start_time).total_seconds()
    else:
        duration_seconds = data['duration']

    # change to minutes
    duration_minutes = round(duration_seconds / 60)

    return start_time, duration_minutes


def save_project_label_map(project_label_map: list):
    with open(CONFIG_PATH+"./project_label_map.json", "w",encoding="utf-8") as f:
        json.dump(project_label_map, f)
