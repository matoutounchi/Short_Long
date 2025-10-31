"""
RSI Divergence Strategy
استراتژی واگرایی RSI با سطوح کلیدی
"""

import pandas as pd
from typing import Optional, Dict
from .base_strategy import BaseStrategy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from indicators.technical_indicators import calculate_rsi, detect_divergence


class RSIDivergenceStrategy(BaseStrategy):
    """
    استراتژی واگرایی RSI
    ورود در واگرایی صعودی/نزولی نزدیک سطوح کلیدی
    """
    
    def __init__(self, rsi_period: int = 14, rsi_oversold: int = 30, 
                 rsi_overbought: int = 70):
        """
        Initialize strategy
        
        Args:
            rsi_period: دوره RSI
            rsi_oversold: سطح بیش‌فروش
            rsi_overbought: سطح بیش‌خرید
        """
        super().__init__("RSI Divergence")
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        تولید سیگنال بر اساس واگرایی RSI
        """
        if len(df) < self.rsi_period + 20:
            return None
        
        # Calculate RSI
        rsi = calculate_rsi(df['close'], self.rsi_period)
        current_rsi = rsi.iloc[-1]
        
        # Detect divergence
        divergence = detect_divergence(df['close'], rsi, lookback=10)
        
        signal = None
        entry_price = df['close'].iloc[-1]
        confidence = 0.0
        
        # Bullish divergence + oversold = Long signal
        if divergence == 'bullish' and current_rsi < self.rsi_overbought:
            signal = 'long'
            confidence = 0.7 if current_rsi < self.rsi_oversold else 0.5
        
        # Bearish divergence + overbought = Short signal
        elif divergence == 'bearish' and current_rsi > self.rsi_oversold:
            signal = 'short'
            confidence = 0.7 if current_rsi > self.rsi_overbought else 0.5
        
        if signal:
            stop_loss = self.calculate_stop_loss(df, entry_price, signal)
            take_profit = self.calculate_take_profit(entry_price, stop_loss, 
                                                     risk_reward_ratio=3.0)
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'rsi': current_rsi
            }
        
        return None
    
    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float,
                           signal: str) -> float:
        """محاسبه حد ضرر"""
        if signal == 'long':
            recent_low = df['low'].rolling(window=10).min().iloc[-1]
            return recent_low * 0.98  # 2% below recent low
        else:  # short
            recent_high = df['high'].rolling(window=10).max().iloc[-1]
            return recent_high * 1.02  # 2% above recent high
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                             risk_reward_ratio: float = 3.0) -> float:
        """محاسبه حد سود"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if entry_price > stop_loss:  # long
            return entry_price + reward
        else:  # short
            return entry_price - reward

