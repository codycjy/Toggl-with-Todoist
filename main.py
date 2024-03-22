import os
import json
import logging
import streamlit as st
from streamlit_tags import st_tags_sidebar
from streamlit_authenticator import Authenticate
import yaml
import toggl
import utils
from todoist import TodoistController
from components import app
with open("pwd.yaml", "r") as file:
    config = yaml.safe_load(file)

if os.path.exists('./project_label_map.json'):
    with open('./project_label_map.json', 'r') as f:
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
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    )


def project_duration_chart(df, options, project_id, index):
    project_for_chart = st.selectbox(
        "Select Project for Chart", options, key="chart_project_select_"+str(index),
        index=index-1

    )
    selected_project_id = project_id[project_for_chart]

    df = toggl.filter_project(df, selected_project_id)

    daily_duration = df.groupby('date')['duration'].sum().reset_index()

    st.write("Project Minutes Spent")
    st.line_chart(daily_duration.set_index('date'), use_container_width=True)


def current_entry_panel():
    if 'toggl_status' not in st.session_state:
        st.session_state.toggl_status = toggl.get_current_entry()

    st.write("Toggl Current Status")
    status = st.session_state.toggl_status
    if not status:
        st.write("No current entry, start a new one?")
        return
    if st.button("Stop"):
        workspace_id = st.session_state.toggl_status['workspace_id']
        entry_id = st.session_state.toggl_status['id']
        toggl.stop_current_entry(workspace_id, entry_id)
        st.session_state.toggl_status = toggl.get_current_entry()

    st.write(f"Description: {status['description']}")
    start_time, duration_minutes = utils.parse_time(status)
    st.write(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"Duration: {duration_minutes} minutes")
    st.session_state.toggl_status = toggl.get_current_entry()


def timer(options, project_id):
    form = st.form("Start a Timer")
    description = form.text_input("Description")
    project = form.selectbox("Project", options)
    submmited = form.form_submit_button('Start')
    if submmited:
        toggl.start_new_entry(description, project_id[project])
        st.rerun()


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
    todoist = TodoistController()
    tasks = todoist.get_all_tasks()
    app(tasks, api)
    daily_duration = df.groupby('date')['duration'].sum().reset_index()
    st.write("Daily Minutes Spent")
    st.line_chart(daily_duration.set_index('date'), use_container_width=True)
    col1, col2 = st.columns(2)
    with col1.container(border=True):
        project_duration_chart(df, options, project_id, 1)
    with col2.container(border=True):
        project_duration_chart(df, options, project_id, 2)


if authentication_status:
    main_page()
