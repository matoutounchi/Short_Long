"""
Volume Confirmed Breakout Strategy
استراتژی شکست با تایید حجم
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from .base_strategy import BaseStrategy


class VolumeBreakoutStrategy(BaseStrategy):
    """
    استراتژی شکست با تایید حجم
    فقط روی شکست‌هایی تمرکز می‌کند که حجم معاملات حداقل 2-3 برابر میانگین باشد
    """
    
    def __init__(self, volume_multiplier: float = 2.0):
        """
        Initialize strategy
        
        Args:
            volume_multiplier: ضریب حجم (حداقل چند برابر میانگین)
        """
        super().__init__("Volume Breakout")
        self.volume_multiplier = volume_multiplier
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        تولید سیگنال بر اساس شکست با حجم بالا
        """
        if len(df) < 20:
            return None
        
        # Calculate average volume
        avg_volume = df['volume'].rolling(window=10).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        # Check if volume is high enough
        if current_volume < avg_volume * self.volume_multiplier:
            return None
        
        # Check for breakout above resistance (for long)
        current_price = df['close'].iloc[-1]
        recent_high = df['high'].rolling(window=20).max().iloc[-2]
        
        # Check for breakdown below support (for short)
        recent_low = df['low'].rolling(window=20).min().iloc[-2]
        
        signal = None
        entry_price = current_price
        
        # Long signal: price breaks above recent high with high volume
        if current_price > recent_high:
            signal = 'long'
            entry_price = current_price
        
        # Short signal: price breaks below recent low with high volume
        elif current_price < recent_low:
            signal = 'short'
            entry_price = current_price
        
        if signal:
            stop_loss = self.calculate_stop_loss(df, entry_price, signal)
            take_profit = self.calculate_take_profit(entry_price, stop_loss)
            
            # Calculate confidence based on volume ratio
            volume_ratio = current_volume / avg_volume
            confidence = min(0.9, 0.5 + (volume_ratio - 2) * 0.1)
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'volume_ratio': volume_ratio
            }
        
        return None
    
    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float, 
                           signal: str) -> float:
        """محاسبه حد ضرر"""
        if signal == 'long':
            # Stop loss below recent low
            recent_low = df['low'].rolling(window=10).min().iloc[-1]
            return recent_low * 0.995  # 0.5% below recent low
        else:  # short
            recent_high = df['high'].rolling(window=10).max().iloc[-1]
            return recent_high * 1.005  # 0.5% above recent high
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                             risk_reward_ratio: float = 2.0) -> float:
        """محاسبه حد سود"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        # For long: take profit above entry
        if entry_price > stop_loss:
            return entry_price + reward
        else:  # short
            return entry_price - reward

