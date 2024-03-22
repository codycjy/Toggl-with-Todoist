from datetime import datetime
import json
def parse_time(data):
    start_time_str = data['start']
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

    # 如果 duration 为负数，计算从 start 到现在的持续时间
    if data['duration'] < 0:
        now = datetime.now(start_time.tzinfo)
        duration_seconds = (now - start_time).total_seconds()
    else:
        duration_seconds = data['duration']

    # 将持续时间转换为分钟，并四舍五入
    duration_minutes = round(duration_seconds / 60)

    return start_time, duration_minutes

def save_project_label_map(project_label_map:list):
    json.dump(project_label_map,open("./project_label_map.json","w"))
