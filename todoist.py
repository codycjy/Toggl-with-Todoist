import logging
from todoist_api_python.api import TodoistAPI
import streamlit as st
from toggl import Toggl


class TodoistController:
    def __init__(self, api_key, toggl: Toggl) -> None:
        self.api = TodoistAPI(api_key)
        self.toggl = toggl
        self.label_project_map=[]

    def set_label_project_map(self, label_project_map):
        self.label_project_map = label_project_map

    def finish_task(self, task_id) -> bool:
        logging.info(f"Finish task {task_id}")
        return self.api.close_task(task_id=task_id)

    def get_all_tasks(self):
        return self.api.get_tasks()

    def start_toggl_entry(self, task):

        project_name = self.api.get_project(task['project_id']).name
        for label in task['labels']:
            if label in self.label_project_map:
                project_name = label
                break
        pid = self.toggl.get_project_id_by_name(project_name)
        self.toggl.start_new_entry(task['content'], task['id'],
                                   tags=task['labels'],
                                   pid=pid,
                                   )
        st.session_state.running_task = task['content']
        logging.info(f"Start toggl entry for {task['content']}")
        st.rerun()


if __name__ == "__main__":
    pass
