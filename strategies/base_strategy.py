"""
Base Strategy Class
کلاس پایه برای تمام استراتژی‌ها
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pandas as pd


class BaseStrategy(ABC):
    """کلاس پایه برای تمام استراتژی‌های معاملاتی"""
    
    def __init__(self, name: str):
        """
        Initialize strategy
        
        Args:
            name: نام استراتژی
        """
        self.name = name
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        تولید سیگنال معاملاتی
        
        Args:
            df: DataFrame با داده‌های OHLCV
            
        Returns:
            Dictionary with signal info:
            {
                'signal': 'long' | 'short' | None,
                'entry_price': float,
                'stop_loss': float,
                'take_profit': float,
                'confidence': float (0-1)
            }
        """
        pass
    
    @abstractmethod
    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float, 
                          signal: str) -> float:
        """
        محاسبه حد ضرر
        
        Args:
            df: DataFrame با داده‌های OHLCV
            entry_price: قیمت ورود
            signal: نوع سیگنال ('long' یا 'short')
            
        Returns:
            Stop loss price
        """
        pass
    
    @abstractmethod
    def calculate_take_profit(self, entry_price: float, stop_loss: float, 
                            risk_reward_ratio: float = 2.0) -> float:
        """
        محاسبه حد سود
        
        Args:
            entry_price: قیمت ورود
            stop_loss: حد ضرر
            risk_reward_ratio: نسبت ریسک به پاداش
            
        Returns:
            Take profit price
        """
        pass

