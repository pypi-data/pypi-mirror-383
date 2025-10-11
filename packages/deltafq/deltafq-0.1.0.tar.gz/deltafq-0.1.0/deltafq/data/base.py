"""数据源基类"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        pass

