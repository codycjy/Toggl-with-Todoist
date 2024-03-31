import logging
from typing import List
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from todoist_api_python.models import Task
from toggl import Toggl
import utils


def process_tasks(tasks: List[Task], filter_str=None):
    processed_data = []
    now = datetime.now()

    for task in tasks:
        task_dict = task.to_dict()
        due = task_dict.get('due')
        due_date = due['date'] if due and 'date' in due else None
        if task.is_completed:
            continue

        if due_date:
            due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
            task_dict['due'] = due_date

            if filter_str == 'Today':
                if due_datetime.date() <= now.date():
                    processed_data.append(task_dict)
            elif filter_str == 'This Week':
                start_week = now - timedelta(days=now.weekday())  # Monday
                end_week = start_week + timedelta(days=6)  # Sunday
                if start_week.date() <= due_datetime.date() <= end_week.date():
                    processed_data.append(task_dict)
            else:
                processed_data.append(task_dict)
        else:
            task_dict['due'] = 'No due'
            if filter_str is None:
                processed_data.append(task_dict)

    return pd.DataFrame(processed_data)


def task_list(tasks, api):
    st.title('Task List')
    filter_option = st.selectbox(
        "Time filter",
        ("Today", "This Week"),
        index=0,
        label_visibility='collapsed',
        placeholder="Select contact method...",
    )

    tasks_df = process_tasks(tasks, filter_option)

    need_rerun = False
    for _, task in tasks_df.iterrows():
        col1, col2,col3, col4 = st.columns([1, 1,8, 1])

        with col1:
            is_selected = st.checkbox('Select Task',
                                      key=f'select_{task["id"]}_{task["due"]}',
                                      label_visibility='collapsed')
            if is_selected:
                logging.info(f"Select {task['content']} id: {task['id']}")
                api.finish_task(task['id'])
                need_rerun = True
        with col2:
            if "running_task" in st.session_state and st.session_state.running_task == task['content']:
                st.write(":hourglass_flowing_sand:")

        with col3:
            st.text(f"{task['due']}    {task['content']}")

        with col4:
            if st.button('Go!', key=f'detail_{task["id"]}'):
                api.start_toggl_entry(task)
                need_rerun = True

    if need_rerun:
        st.rerun()


def current_entry_panel(toggl: Toggl):
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
        st.rerun()

    st.write(f"Description: {status['description']}")
    start_time, duration_minutes = utils.parse_time(status)
    st.write(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"Duration: {duration_minutes} minutes")
    st.session_state.running_task = status['description']


def project_duration_chart(toggl, df, options, project_id, index):
    project_for_chart = st.selectbox(
        "Select Project for Chart", options, key="chart_project_select_"+str(index),
        index=index-1
    )
    try:
        selected_project_id = project_id[project_for_chart]
    except KeyError:
        st.write(f"Project {project_for_chart} not found")
        return


    df = toggl.filter_project(df, selected_project_id)

    daily_duration = df.groupby('date')['duration'].sum().reset_index()
    if daily_duration.empty:
        st.write(f"No data for Project: {project_for_chart}")
        return

    st.write("Project Minutes Spent")
    st.line_chart(daily_duration.set_index('date'), use_container_width=True)


def timer(toggl, options, project_id):
    form = st.form("Start a Timer")
    description = form.text_input("Description")
    project = form.selectbox("Project", options)
    submmited = form.form_submit_button('Start')
    if submmited:
        toggl.start_new_entry(description, project_id[project])
        st.rerun()


def daily_duration_chart(df):
    daily_duration = df.groupby('date')['duration'].sum().reset_index()
    st.write("Daily Minutes Spent")
    st.line_chart(daily_duration.set_index('date'), use_container_width=True)
