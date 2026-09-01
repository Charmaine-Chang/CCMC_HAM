"""通用小工具"""
from datetime import date, datetime, timedelta


def parse_date(value, default=None):
    if not value:
        return default
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return default


def parse_datetime(value, default=None):
    if not value:
        return default
    value = value.strip()
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M'):
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return parse_date(value, default)


def split_names(raw):
    """把多行/逗号分隔的姓名解析为列表。"""
    names = []
    for part in (raw or '').replace('，', ',').split(','):
        for line in part.splitlines():
            name = line.strip()
            if name and name not in names:
                names.append(name)
    return names


def month_grid(year, month):
    """返回一个日历月 6x7 网格（含前后月补位日期）。"""
    first = date(year, month, 1)
    start = first - timedelta(days=first.weekday())
    weeks = []
    cursor = start
    for _ in range(6):
        week = []
        for _ in range(7):
            week.append(cursor)
            cursor += timedelta(days=1)
        weeks.append(week)
        if cursor.month != month and cursor > first:
            break
    return weeks


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

