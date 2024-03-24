import logging
import time
import os
import json
from datetime import datetime

from requests.auth import HTTPBasicAuth
import requests
import pandas as pd
import streamlit as st


TOGGL_API_ENDPOINT = "https://api.track.toggl.com/api/v9"
def get_session():
    api_key = os.getenv("TOGGL_API", "")
    if not api_key:
        logging.error("NO TOGGL_API KEY FOUND")
    sess = requests.session()
    sess.auth = HTTPBasicAuth(api_key, "api_token")
    return sess


@st.cache_data
def get_workspace_project():
    sess = get_session()
    workspace_id = get_workspace_id()
    url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
    sess = get_session()
    response = sess.get(url)
    return response.json()


@st.cache_data
def get_workspace_id():
    workspace_url = f"{TOGGL_API_ENDPOINT}/workspaces"
    sess = get_session()
    response = sess.get(workspace_url)
    data = response.json()
    workspace_id = data[0]['id']
    return workspace_id

# @st.cache_data


def get_all_entries():
    sess = get_session()
    workspace_id = get_workspace_id()
    response = sess.get(
        f"{TOGGL_API_ENDPOINT}/projects/"+f"{workspace_id}")
    time_entry_url = f"{TOGGL_API_ENDPOINT}/me/time_entries"
    response = sess.get(time_entry_url)
    df = pd.DataFrame(response.json())
    df['start'] = pd.to_datetime(df['start'])
    df['date'] = df['start'].dt.date
    df['duration'] = df['duration'] / 60
    df = df[df['duration'] > 0]

    project_ids = df['project_id'].unique()

    result_df = pd.DataFrame()

    for project_id in project_ids:
        project_df = df[df['project_id'] == project_id]
        min_date = project_df['date'].min(
        ) if not project_df['date'].empty else datetime.today().date()
        max_date = project_df['date'].max(
        ) if not project_df['date'].empty else datetime.today().date()
        all_dates = pd.date_range(min_date, max_date, freq='D').date

        missing_dates = set(all_dates) - set(project_df['date'])

        missing_data = [{'project_id': project_id, 'date': date,
                         'duration': 0} for date in missing_dates]
        missing_df = pd.DataFrame(missing_data)

        project_df = pd.concat([project_df, missing_df], ignore_index=True)

        result_df = pd.concat([result_df, project_df], ignore_index=True)

    return result_df


def filter_project(df, project_id):
    return df[df['project_id'] == project_id]


def get_current_entry():
    sess = get_session()
    entry_url = f"{TOGGL_API_ENDPOINT}/me/time_entries/current"
    response = sess.get(entry_url)
    if response.status_code != 200:
        return {}
    return response.json()


def start_new_entry(description, project_id, **kwargs):
    sess = get_session()
    workspace_id = get_workspace_id()
    entry_url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/time_entries"
    now = time.time()
    start_rfc3339 = datetime.utcfromtimestamp(
        now).isoformat(timespec="seconds") + "Z"
    data = {
        "description": description,
        "duration": -1,  # * int(now),
        "start": start_rfc3339,
        "stop": None,
        "pid": project_id,
        "workspace_id": workspace_id,
        "created_with": "python-toggl-api"

    }
    data.update(kwargs)
    response = sess.post(entry_url, json=data)
    if response.status_code != 200:
        st.write(response.text)
    return response.json()


def stop_current_entry(workspace_id, time_entry_id):
    sess = get_session()
    entry_url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop"
    response = sess.patch(entry_url)
    response.raise_for_status()
    return response.json()


def get_all_tags():
    sess = get_session()
    workspace_id = get_workspace_id()
    url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/tags"
    response = sess.get(url)
    return response.json()


def find_project_id_by_name(project_name, all_projects):
    for project in all_projects:
        if project['name'] == project_name:
            return project['id']
    return None


@st.cache_data
def get_all_projects():
    sess = get_session()
    workspace_id = get_workspace_id()
    url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
    response = sess.get(url)
    return response.json()


def create_new_project(name):
    sess = get_session()
    workspace_id = get_workspace_id()
    url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
    data = {
        "name": name,
        "wid": workspace_id
    }
    response = sess.post(url, json=data)
    return response.json()


def get_project_id_by_name(name):
    projects = get_all_projects()
    pid = find_project_id_by_name(name, projects)
    if pid:
        return pid
    return create_new_project(name)['id']


def save_project_label_map(project_label_map: list):
    with open("./project_label_map.json", "w",encoding="utf-8") as f:
        json.dump(project_label_map, f)


if __name__ == "__main__":
    pass
