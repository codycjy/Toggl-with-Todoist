import os
import json
import logging
import streamlit as st
from streamlit_tags import st_tags_sidebar
from streamlit_authenticator import Authenticate
from streamlit_autorefresh import st_autorefresh
import yaml
import toggl
import utils
from todoist import TodoistController
from components import daily_duration_chart, task_list, current_entry_panel, project_duration_chart
from components import timer
from const import CONFIG_PATH, MAP_PATH

# Get auth info
with open(os.path.join(CONFIG_PATH, "pwd.yaml"), "r",encoding="utf-8") as file:
    config = yaml.safe_load(file)
if os.path.exists(MAP_PATH):
    with open(MAP_PATH, 'r',encoding="utf-8") as f:
        project_label_map = json.load(f)
else:
    project_label_map = []

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

api = TodoistController()
if authentication_status:
    st.title('Toggl Dashboard')
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    )


def main_page():
    global project_label_map
    project_id = {}
    options = []
    projects = toggl.get_workspace_project()

    for p in projects:
        project_id[p['name']] = p['id']
        options.append(p['name'])
    with st.sidebar:
        timer(options, project_id)

        with st.container(border=True):
            keyword = st_tags_sidebar(label='Tag Project Map',
                                      text='Press enter to add more',
                                      value=project_label_map,
                                      key="afrfae")
            if keyword:
                utils.save_project_label_map(keyword)
                project_label_map = keyword
                api.set_label_project_map(project_label_map)

        with st.container(border=True):
            current_entry_panel()

    df = toggl.get_all_entries()
    tasks = api.get_all_tasks()

    task_list(tasks, api)
    daily_duration_chart(df)
    col1, col2 = st.columns(2)
    with col1.container(border=True):
        project_duration_chart(df, options, project_id, 1)
    with col2.container(border=True):
        project_duration_chart(df, options, project_id, 2)


# Set auto refresh
st_autorefresh(interval=30*1000,  key="fizzbuzzcounter")

if authentication_status:
    main_page()
