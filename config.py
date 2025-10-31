"""
Configuration file for Short/Long Trading System
تنظیمات سیستم معاملاتی Short/Long
"""

# Exchange Configuration
EXCHANGE = "binance"
BASE_CURRENCY = "USDT"

# Trading Pairs
TRADING_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "DOGE/USDT",
]

# Timeframe
TIMEFRAME = "10m"  # 10 minutes

# Strategy Parameters
STRATEGY_CONFIG = {
    # Volume Confirmed Breakout
    "volume_multiplier": 2.0,  # حداقل 2 برابر میانگین حجم
    
    # RSI Divergence
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    
    # Bollinger Bands
    "bb_period": 20,
    "bb_std": 2.0,
    
    # EMA Crossover
    "ema_fast": 5,
    "ema_slow": 20,
    
    # ATR
    "atr_period": 14,
    
    # MACD
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
}

# Risk Management
RISK_CONFIG = {
    "max_position_size": 0.02,  # 2% of capital per trade
    "max_positions": 3,  # Maximum simultaneous positions
    "risk_reward_ratio": 2.0,  # Minimum 1:2
    "stop_loss_atr_multiplier": 1.3,
}

# Data Configuration
DATA_CONFIG = {
    "lookback_days": 30,
    "update_interval": 10,  # seconds
}

# Logging
LOG_CONFIG = {
    "level": "INFO",
    "file": "logs/trading.log",
    "console": True,
}

