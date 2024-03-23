import time
import streamlit as st
import pandas as pd


def process_tasks(tasks):
    processed_data = []
    for task in tasks:
        task_dict = task.to_dict()
        due = task_dict.get('due')
        task_dict['due'] = due['date'] if due and 'date' in due else 'No due    '
        processed_data.append(task_dict)
    return pd.DataFrame(processed_data)


def app(tasks, api):
    st.title('Task List')
    tasks_df = process_tasks(tasks)

    tasks_to_finish = []

    need_rerun = False
    for _, task in tasks_df.iterrows():
        col1, col2, col3 = st.columns([1, 4, 1])

        t = int(time.time())
        with col1:
            is_selected = st.checkbox(
                'Select Task', key=f'select_{task["id"]}_{t}', label_visibility='collapsed')
            # use t to identify recurrent task

        with col2:
            st.text(f"{task['due']}    {task['content']}")

        with col3:
            if st.button('Go!', key=f'detail_{task["id"]}'):
                api.start_toggl_entry(task)
                need_rerun = True

        if is_selected:
            tasks_to_finish.append(task['id'])

    for task_id in tasks_to_finish:
        api.finish_task(task_id)

    if tasks_to_finish or need_rerun:
        st.rerun()
