from datetime import datetime, timezone
from enum import Enum


class TimeFormat(Enum):
    """常见时间格式枚举"""
    YYYYMMDD = "%Y%m%d"  # 20231025
    YYYY_MM_DD = "%Y-%m-%d"  # 2023-10-25
    YYYYMMDD_HHMMSS = "%Y%m%d%H%M%S"  # 20231025143045
    YYYY_MM_DD_HH_MM_SS = "%Y-%m-%d %H:%M:%S"  # 2023-10-25 14:30:45
    HHMMSS = "%H%M%S"  # 143045
    HH_MM_SS = "%H:%M:%S"  # 14:30:45
    MONTH_DAY_YEAR = "%b %d, %Y"  # Oct 25, 2023 (英文缩写月)
    WEEKDAY_MONTH_DAY = "%A, %B %d"  # Wednesday, October 25


def get_utc_date_str(fmt: str = TimeFormat.YYYYMMDD.value) -> str:
    """获取当前UTC日期，默认格式为YYYYMMDD"""
    return datetime.now(timezone.utc).strftime(fmt)
