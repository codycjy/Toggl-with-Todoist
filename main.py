import os
import json
import logging
import streamlit as st
from streamlit_tags import st_tags_sidebar
from streamlit_authenticator import Authenticate
from streamlit_autorefresh import st_autorefresh
import yaml
from toggl import Toggl
import utils
from todoist import TodoistController
from components import daily_duration_chart, task_list, current_entry_panel, project_duration_chart
from components import timer
from const import CONFIG_PATH, MAP_PATH

st.set_page_config(
    page_title="Toggl with Todoist",
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded",
)

# Get auth info
pwd_config_path = os.path.join(CONFIG_PATH, "pwd.yaml")
pwd_config_exist = os.path.exists(pwd_config_path)
if not pwd_config_exist:
    st.error(
        "Please create a pwd.yaml file following the instructions in the README.md file.")
    authentication_status = None
else:
    with open(os.path.join(CONFIG_PATH, "pwd.yaml"), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    name, authentication_status, username = authenticator.login()


# TODO: maybe add a lock for json?
if os.path.exists(MAP_PATH):
    with open(MAP_PATH, 'r', encoding="utf-8") as f:
        project_label_map = json.load(f)
else:
    project_label_map = []

st.session_state.project_label_map = project_label_map

if authentication_status:
    pass
elif authentication_status is False:
    st.error('Username/password is incorrect')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s')

api_dict = utils.load_env()

if api_dict:

    if 'toggl' not in st.session_state:
        st.session_state.toggl = Toggl(api_dict['TOGGL_API'])

    if 'todoist' not in st.session_state:
        st.session_state.todoist = TodoistController(
            api_dict['TODOIST_API'],
            st.session_state.toggl
        )

else:
    authentication_status = None


def main_page(toggl: Toggl, todoist: TodoistController):
    global project_label_map
    df = toggl.get_all_entries()
    tasks = todoist.get_all_tasks()
    options, project_id = toggl.get_workspace_project()

    with st.sidebar:
        timer(toggl, options, project_id)

        with st.container(border=True):
            keyword = st_tags_sidebar(label='Tag Project Map',
                                      text='Press enter to add more',
                                      value=project_label_map,
                                      key="afrfae")
            old_project_label_map = st.session_state.get(
                'project_label_map', [])
            if keyword != old_project_label_map:
                utils.save_project_label_map(keyword)
                project_label_map = keyword
                todoist.set_label_project_map(project_label_map)

        with st.container(border=True):
            current_entry_panel(toggl)

    task_list(tasks, todoist)
    st.title('Toggl Dashboard')
    daily_duration_chart(df)
    col1, col2 = st.columns(2)
    with col1.container(border=True):
        project_duration_chart(toggl, df, options, project_id, 1)
    with col2.container(border=True):
        project_duration_chart(toggl, df, options, project_id, 2)


# Set auto refresh 30s
st_autorefresh(interval=30*1000,  key="fizzbuzzcounter")

if authentication_status:
    toggl = st.session_state.toggl
    todoist = st.session_state.todoist
    main_page(toggl, todoist)
