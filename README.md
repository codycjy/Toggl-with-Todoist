# Toggl-with-Todoist

## Why this project
This application integrates the strengths of two excellent tools: Toggl and Todoist. While Toggl excels in time tracking, it lacks robust task management features. Conversely, Todoist is great for managing tasks but doesn’t offer time tracking. By combining these two, users can leverage the best of both worlds.

## What can you do with this app
- Start a Toggl time entry directly from a Todoist task.
- View time entry charts by day and by project.
- Use the label map func which allow user add projects in toggl regardless of todoist project limitation.

## How to use
### Docker compose(recommended)
1. Obtain your API keys from [Todoist](https://todoist.com/) and [Toggl](https://toggl.com/).
2. Download compose and config file
   ```bash
   mkdir config
   wget -O config/docker-compose.yaml https://github.com/codycjy/Toggl-with-Todoist/raw/main/docker-compose.yaml
   wget -O config/.env https://github.com/codycjy/Toggl-with-Todoist/raw/main/.example.env
   wget -O config/pwd.example https://github.com/codycjy/Toggl-with-Todoist/raw/main/pwd.yaml.example

   ```
3. Fill in the API keys and user information in the `pwd.yaml` and `.env` files.
4. Launch the application using Docker:
   ```bash
   docker compose up -d
   ```
5. Access the application at `http://localhost:8501`.

### Run it directly
1. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
2. Obtain your API keys from [Todoist](https://todoist.com/) and [Toggl](https://toggl.com/).
3. Set env
   ```bash
   export TOGGL_API=YOUR_API
   export TODOIST_API=YOUR_API
   ```
4. Run the app
   ```bash
   streamlit run main.py
   ```

# TODO
- [ ] Better UI 
- [ ] Save status in session for better usage
- [x] Filter for Tasks

# Contribution
Welcome any kinds of contributions.
Feel free to open an issue :)
