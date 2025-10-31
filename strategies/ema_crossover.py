"""
EMA Crossover Strategy with Volume Confirmation
استراتژی کراس EMA با تایید حجم
"""

import pandas as pd
from typing import Optional, Dict
from .base_strategy import BaseStrategy
from indicators.technical_indicators import calculate_ema


class EMACrossoverStrategy(BaseStrategy):
    """
    استراتژی کراس EMA
    ورود در کراس صعودی/نزولی با تایید حجم
    """
    
    def __init__(self, fast_period: int = 5, slow_period: int = 20,
                 volume_multiplier: float = 1.5):
        """
        Initialize strategy
        
        Args:
            fast_period: دوره EMA سریع
            slow_period: دوره EMA کند
            volume_multiplier: حداقل ضریب حجم
        """
        super().__init__("EMA Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.volume_multiplier = volume_multiplier
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        تولید سیگنال بر اساس کراس EMA
        """
        if len(df) < self.slow_period + 5:
            return None
        
        # Calculate EMAs
        ema_fast = calculate_ema(df['close'], self.fast_period)
        ema_slow = calculate_ema(df['close'], self.slow_period)
        
        current_fast = ema_fast.iloc[-1]
        current_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2]
        prev_slow = ema_slow.iloc[-2]
        
        # Check volume
        avg_volume = df['volume'].rolling(window=10).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        if current_volume < avg_volume * self.volume_multiplier:
            return None
        
        # Check for crossover
        signal = None
        entry_price = df['close'].iloc[-1]
        confidence = 0.6
        
        # Bullish crossover: fast crosses above slow
        if prev_fast <= prev_slow and current_fast > current_slow:
            signal = 'long'
            confidence = 0.7 if current_fast > current_slow * 1.01 else 0.5
        
        # Bearish crossover: fast crosses below slow
        elif prev_fast >= prev_slow and current_fast < current_slow:
            signal = 'short'
            confidence = 0.7 if current_fast < current_slow * 0.99 else 0.5
        
        if signal:
            stop_loss = self.calculate_stop_loss(df, entry_price, signal)
            take_profit = self.calculate_take_profit(entry_price, stop_loss, 
                                                     risk_reward_ratio=2.5)
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'ema_fast': current_fast,
                'ema_slow': current_slow
            }
        
        return None
    
    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float,
                           signal: str) -> float:
        """محاسبه حد ضرر"""
        if signal == 'long':
            recent_low = df['low'].rolling(window=10).min().iloc[-1]
            return recent_low * 0.995
        else:  # short
            recent_high = df['high'].rolling(window=10).max().iloc[-1]
            return recent_high * 1.005
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                             risk_reward_ratio: float = 2.5) -> float:
        """محاسبه حد سود"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if entry_price > stop_loss:  # long
            return entry_price + reward
        else:  # short
            return entry_price - reward

