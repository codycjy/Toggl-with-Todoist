from datetime import datetime
import json
import os
import streamlit as st


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
    json_path=os.path.join(CONFIG_PATH,"./project_label_map.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(project_label_map, f)


def load_env():
    toggle_api_key = os.getenv('TOGGL_API')
    todoist_api_key = os.getenv('TODOIST_API')
    if not (toggle_api_key and todoist_api_key):
        st.error("Please set the TOGGL_API and TODOIST_API in env")
        return {}
    return {
        'TOGGL_API': toggle_api_key,
        'TODOIST_API': todoist_api_key,
    }
