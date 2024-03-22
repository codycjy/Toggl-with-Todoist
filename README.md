# Toggl-with-Todoist

## Why this project
This application integrates the strengths of two excellent tools: Toggl and Todoist. While Toggl excels in time tracking, it lacks robust task management features. Conversely, Todoist is great for managing tasks but doesn’t offer time tracking. By combining these two, users can leverage the best of both worlds.

## What can you do with this app
- Start a Toggl time entry directly from a Todoist task.
- View time entry charts by day and by project.
- Use the label map func which allow user add projects in toggl regardless of todoist project limitation.

## How to use
### Run it directly
1. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
2. Set env
   ```bash
   export TOGGL_API=YOUR_API
   export TODOIST_API=YOUR_API
   ```
3. Run the app
   ```bash
   streamlit run main.py
   ```

### Docker compose
1. Obtain your API keys from [Todoist](https://todoist.com/) and [Toggl](https://toggl.com/).
2. Clone the repository:
   ```bash
   git clone https://github.com/codycjy/Toggl-with-Todoist.git
   ```
3. Copy the example configuration files and rename them:
   ```
   cp pwd.yaml.example pwd.yaml
   cp .env.example .env
   ```
4. Fill in the API keys and user information in the `pwd.yaml` and `.env` files.
5. Launch the application using Docker:
   ```bash
   docker compose up -d
   ```
6. Access the application at `http://localhost:8501`.

# TODO
- [ ] Better UI 

# Contribution
Welcome any kinds of contributions.
