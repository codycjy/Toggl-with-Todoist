import logging
import time
import json
from datetime import datetime, timedelta

from requests.auth import HTTPBasicAuth
import requests
import pandas as pd
import streamlit as st


TOGGL_API_ENDPOINT = "https://api.track.toggl.com/api/v9"


class Toggl:
    def __init__(self, api_key) -> None:
        sess = requests.session()
        sess.auth = HTTPBasicAuth(api_key, "api_token")
        self.sess = sess
        self.df = pd.DataFrame()

    def get_workspace_project(_self):
        if len(_self.df) == 0:
            _self.get_all_entries()
        df = _self.df
        df = df.dropna(subset=['description', 'project_id'])

        project_ids = df['project_id'].unique().tolist()

        sess = _self.sess
        workspace_id = _self.get_workspace_id()
        url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
        response = sess.get(url)
        projects = response.json()
        project_name_map = {p['name']: p['id']
                            for p in projects if p['id'] in project_ids}
        project_name_list = list(project_name_map.keys())
        return project_name_list, project_name_map

    @st.cache_data
    def get_workspace_id(_self):
        workspace_url = f"{TOGGL_API_ENDPOINT}/workspaces"
        sess = _self.sess
        response = sess.get(workspace_url)
        if response.status_code != 200:
            st.warning("Failed to get workspace ID")
        data = response.json()
        workspace_id = data[0]['id']
        return workspace_id

    def get_all_entries(_self):
        sess = _self.sess
        workspace_id = _self.get_workspace_id()
        response = sess.get(f"{TOGGL_API_ENDPOINT}/projects/{workspace_id}")
        time_entry_url = f"{TOGGL_API_ENDPOINT}/me/time_entries"
        response = sess.get(time_entry_url)
        df = pd.DataFrame(response.json())
        df['start'] = pd.to_datetime(df['start'])
        df['date'] = df['start'].dt.date
        df['duration'] = df['duration'] / 60
        df = df[df['duration'] > 0]

        project_ids = df['project_id'].unique()

        result_df = pd.DataFrame()

        # Get the date range for the last 7 days including today
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=6)
        all_dates = pd.date_range(start_date, end_date, freq='D').date

        for project_id in project_ids:
            project_df = df[df['project_id'] == project_id]

            # Find missing dates within the 7-day range
            project_dates = set(project_df['date'])
            missing_dates = set(all_dates) - project_dates

            # Fill missing dates with zero duration
            missing_data = [{'project_id': project_id, 'date': date,
                             'duration': 0} for date in missing_dates]
            missing_df = pd.DataFrame(missing_data)

            project_df = pd.concat([project_df, missing_df], ignore_index=True)

            # Ensure the DataFrame covers the 7-day span
            project_df = project_df[project_df['date'].isin(all_dates)]

            result_df = pd.concat([result_df, project_df], ignore_index=True)
        _self.df = result_df

        return result_df

    @staticmethod
    def filter_project(df, project_id):
        return df[df['project_id'] == project_id]

    def get_current_entry(self):
        sess = self.sess
        entry_url = f"{TOGGL_API_ENDPOINT}/me/time_entries/current"
        logging.info("Getting current entry")
        response = sess.get(entry_url)
        if response.status_code != 200:
            return {}
        return response.json()

    def start_new_entry(self, description, project_id, **kwargs):
        sess = self.sess
        workspace_id = self.get_workspace_id()
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
        logging.info(f"Starting new entry {description}")
        response = sess.post(entry_url, json=data)
        return response.json()

    def stop_current_entry(self, workspace_id, time_entry_id):
        sess = self.sess
        entry_url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}\
        /time_entries/{time_entry_id}/stop"
        logging.info(f"Stopping current entry ID:{time_entry_id}")
        response = sess.patch(entry_url)
        if response.status_code != 200:
            logging.error(response.text)
            return {}
        return response.json()

    def get_all_tags(self):
        sess = self.sess
        workspace_id = self.get_workspace_id()
        url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/tags"
        response = sess.get(url)
        return response.json()

    @staticmethod
    def find_project_id_by_name(project_name, all_projects):
        for project in all_projects:
            if project['name'] == project_name:
                return project['id']
        return None

    @st.cache_data
    def get_all_projects(_self):
        sess = _self.sess
        workspace_id = _self.get_workspace_id()
        logging.info(f"Getting all projects for workspace {workspace_id}")
        url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
        response = sess.get(url)
        return response.json()

    def create_new_project(self, name):
        sess = self.sess
        workspace_id = self.get_workspace_id()
        logging.info(f"Creating new project {name}")
        url = f"{TOGGL_API_ENDPOINT}/workspaces/{workspace_id}/projects"
        data = {
            "name": name,
            "wid": workspace_id
        }
        response = sess.post(url, json=data)
        return response.json()

    def get_project_id_by_name(self, name):
        projects = self.get_all_projects()
        pid = self.find_project_id_by_name(name, projects)
        if pid:
            return pid
        return self.create_new_project(name)['id']


def save_project_label_map(project_label_map: list):
    with open("./project_label_map.json", "w", encoding="utf-8") as f:
        json.dump(project_label_map, f)


if __name__ == "__main__":
    pass
