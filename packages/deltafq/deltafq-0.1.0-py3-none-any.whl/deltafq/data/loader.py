"""数据加载器"""

import pandas as pd
import numpy as np
from typing import Optional


def get_stock_daily(
    symbol: str,
    start: str,
    end: str,
    source: str = "mock"
) -> pd.DataFrame:
    """获取股票日线数据
    
    Args:
        symbol: 股票代码
        start: 开始日期
        end: 结束日期
        source: 数据源，目前支持 'mock'
        
    Returns:
        包含OHLCV数据的DataFrame
    """
    dates = pd.date_range(start=start, end=end, freq='B')
    n = len(dates)
    base_price = 100 + np.random.randn(n).cumsum()
    open_price = base_price + np.random.randn(n) * 0.5
    close_price = base_price + np.random.randn(n) * 0.5
    high_price = np.maximum(open_price, close_price) + np.abs(np.random.randn(n) * 0.5)
    low_price = np.minimum(open_price, close_price) - np.abs(np.random.randn(n) * 0.5)
    
    data = pd.DataFrame({
        'open': open_price,
        'high': high_price,
        'low': low_price,
        'close': close_price,
        'volume': np.random.randint(1000000, 10000000, n),
    }, index=dates)
    
    data.index.name = 'date'
    return data


def get_stock_minute(
    symbol: str,
    start: str,
    end: str,
    freq: str = '1min'
) -> pd.DataFrame:
    """获取股票分钟数据
    
    Args:
        symbol: 股票代码
        start: 开始日期
        end: 结束日期
        freq: 频率，如 '1min', '5min'
        
    Returns:
        包含OHLCV数据的DataFrame
    """
    raise NotImplementedError("分钟数据功能待实现")

