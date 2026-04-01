from datetime import datetime, timedelta
import re

def parse_date(date_str):
    # 尝试解析带时间的格式（如 2025/5/16 13:30:14）
    try:
        return datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
    except ValueError:
        pass
    
    # 尝试解析不带时间的格式（如 2025/5/16）
    try:
        return datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        pass
    
    # 处理中文格式（如 5月16日）
    match = re.match(r"(\d{1,2})月(\d{1,2})日", date_str)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        # 假设年份为当前年（若跨年需额外处理）
        current_year = datetime.now().year
        return datetime(current_year, month, day)
    
    # 尝试解析 ISO 格式（如 2025-05-16）
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    # 尝试解析英文格式（如 16th May 2025）
    try:
        return datetime.strptime(date_str, "%dth %b %Y")
    except ValueError:
        pass

    # 其他格式可在此扩展
    return None  # 无法解析的日期返回 None