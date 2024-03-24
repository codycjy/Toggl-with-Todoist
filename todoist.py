import os
import logging
from todoist_api_python.api import TodoistAPI
import streamlit as st
import toggl


class TodoistController:
    label_project_map = ["Beigene", "Exercise", "FinalPaper",
                         "Japanese", "Photo", "Yaocheng", "Project"]

    def __init__(self) -> None:
        api_key = os.getenv("TODOIST_API")
        if not api_key:
            logging.error("No TODOIST_API KEY FOUND")
        self.api = TodoistAPI(api_key)

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
        pid = toggl.get_project_id_by_name(project_name)
        toggl.start_new_entry(task['content'], task['id'],
                              tags=task['labels'],
                              pid=pid,
                              )
        logging.info(f"Start toggl entry for {task['content']}")
        st.rerun()


if __name__ == "__main__":
    pass
