"""数据获取和管理模块"""

from deltafq.data.base import DataSource
from deltafq.data.loader import get_stock_daily, get_stock_minute

__all__ = ["DataSource", "get_stock_daily", "get_stock_minute"]

