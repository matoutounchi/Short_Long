"""
Bollinger Bands Squeeze Breakout Strategy
استراتژی شکست از باندهای بولینجر فشرده
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from .base_strategy import BaseStrategy
from indicators.technical_indicators import calculate_bollinger_bands, calculate_atr, calculate_macd


class BollingerSqueezeStrategy(BaseStrategy):
    """
    استراتژی ATR Squeeze Breakout
    شناسایی دوره‌های آرامش قبل از طوفان
    """
    
    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, 
                 atr_period: int = 14):
        """
        Initialize strategy
        
        Args:
            bb_period: دوره باندهای بولینجر
            bb_std: انحراف معیار
            atr_period: دوره ATR
        """
        super().__init__("Bollinger Squeeze")
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.atr_period = atr_period
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        تولید سیگنال بر اساس فشردگی و شکست باندهای بولینجر
        """
        if len(df) < max(self.bb_period, self.atr_period) + 20:
            return None
        
        # Calculate indicators
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
            df['close'], self.bb_period, self.bb_std
        )
        atr = calculate_atr(df['high'], df['low'], df['close'], self.atr_period)
        macd, signal, _ = calculate_macd(df['close'])
        
        current_price = df['close'].iloc[-1]
        current_upper = bb_upper.iloc[-1]
        current_lower = bb_lower.iloc[-1]
        
        # Check for squeeze (narrow bands)
        bb_width = (current_upper - current_lower) / current_price
        avg_bb_width = ((bb_upper - bb_lower) / df['close']).rolling(window=15).mean().iloc[-1]
        
        # Check for low ATR (low volatility)
        current_atr = atr.iloc[-1]
        avg_atr = atr.rolling(window=15).mean().iloc[-1]
        
        # Squeeze condition: narrow bands and low ATR
        is_squeeze = bb_width < avg_bb_width * 0.7 and current_atr < avg_atr * 0.8
        
        if not is_squeeze:
            return None
        
        # Check for breakout
        signal = None
        entry_price = current_price
        confidence = 0.6
        
        # MACD confirmation
        macd_above = macd.iloc[-1] > signal.iloc[-1]
        macd_cross = macd.iloc[-1] > 0 if macd_above else macd.iloc[-1] < 0
        
        # Long: breakout above upper band with MACD confirmation
        if current_price > current_upper and macd_cross and macd_above:
            signal = 'long'
            confidence = 0.8 if df['volume'].iloc[-1] > df['volume'].rolling(window=10).mean().iloc[-1] else 0.6
        
        # Short: breakdown below lower band with MACD confirmation
        elif current_price < current_lower and macd_cross and not macd_above:
            signal = 'short'
            confidence = 0.8 if df['volume'].iloc[-1] > df['volume'].rolling(window=10).mean().iloc[-1] else 0.6
        
        if signal:
            stop_loss = self.calculate_stop_loss(df, entry_price, signal)
            take_profit = self.calculate_take_profit(entry_price, stop_loss)
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'bb_width': bb_width,
                'atr_ratio': current_atr / avg_atr
            }
        
        return None
    
    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float,
                           signal: str) -> float:
        """محاسبه حد ضرر با استفاده از ATR"""
        atr = calculate_atr(df['high'], df['low'], df['close'], self.atr_period)
        current_atr = atr.iloc[-1]
        
        if signal == 'long':
            return entry_price - (current_atr * 1.3)
        else:  # short
            return entry_price + (current_atr * 1.3)
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                             risk_reward_ratio: float = 2.0) -> float:
        """محاسبه حد سود"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if entry_price > stop_loss:  # long
            return entry_price + reward
        else:  # short
            return entry_price - reward

