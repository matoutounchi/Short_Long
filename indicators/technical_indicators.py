"""
Technical Indicators
اندیکاتورهای تکنیکال برای تحلیل بازار
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    محاسبه Relative Strength Index (RSI)
    
    Args:
        prices: سری قیمت‌ها
        period: دوره محاسبه
        
    Returns:
        RSI values
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    محاسبه Exponential Moving Average (EMA)
    
    Args:
        prices: سری قیمت‌ها
        period: دوره محاسبه
        
    Returns:
        EMA values
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    محاسبه MACD
    
    Args:
        prices: سری قیمت‌ها
        fast: دوره EMA سریع
        slow: دوره EMA کند
        signal: دوره signal line
        
    Returns:
        MACD line, Signal line, Histogram
    """
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                               std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    محاسبه Bollinger Bands
    
    Args:
        prices: سری قیمت‌ها
        period: دوره محاسبه
        std_dev: انحراف معیار
        
    Returns:
        Upper band, Middle band (SMA), Lower band
    """
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return upper, middle, lower


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> pd.Series:
    """
    محاسبه Average True Range (ATR)
    
    Args:
        high: سری بالاترین قیمت
        low: سری پایین‌ترین قیمت
        close: سری قیمت بسته شدن
        period: دوره محاسبه
        
    Returns:
        ATR values
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                         k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    محاسبه Stochastic Oscillator
    
    Args:
        high: سری بالاترین قیمت
        low: سری پایین‌ترین قیمت
        close: سری قیمت بسته شدن
        k_period: دوره %K
        d_period: دوره %D
        
    Returns:
        %K, %D
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period).mean()
    
    return k, d


def detect_divergence(prices: pd.Series, indicator: pd.Series, 
                     lookback: int = 10) -> Optional[str]:
    """
    تشخیص واگرایی (Divergence)
    
    Args:
        prices: سری قیمت‌ها
        indicator: سری اندیکاتور (مثلاً RSI)
        lookback: تعداد کندل‌های بررسی
        
    Returns:
        'bullish', 'bearish', or None
    """
    if len(prices) < lookback * 2:
        return None
    
    recent_prices = prices.iloc[-lookback:]
    recent_indicator = indicator.iloc[-lookback:]
    
    # Check for bullish divergence
    price_lows = recent_prices.nsmallest(2)
    indicator_lows = recent_indicator.loc[price_lows.index]
    
    if len(price_lows) >= 2 and len(indicator_lows) >= 2:
        if price_lows.iloc[-1] > price_lows.iloc[-2] and \
           indicator_lows.iloc[-1] < indicator_lows.iloc[-2]:
            return 'bullish'
    
    # Check for bearish divergence
    price_highs = recent_prices.nlargest(2)
    indicator_highs = recent_indicator.loc[price_highs.index]
    
    if len(price_highs) >= 2 and len(indicator_highs) >= 2:
        if price_highs.iloc[-1] < price_highs.iloc[-2] and \
           indicator_highs.iloc[-1] > indicator_highs.iloc[-2]:
            return 'bearish'
    
    return None


def calculate_volume_profile(df: pd.DataFrame, bins: int = 20) -> dict:
    """
    محاسبه Volume Profile
    
    Args:
        df: DataFrame با ستون‌های high, low, volume
        bins: تعداد binها
        
    Returns:
        Dictionary with volume profile data
    """
    price_range = df['high'].max() - df['low'].min()
    bin_size = price_range / bins
    
    volume_profile = {}
    
    for _, row in df.iterrows():
        price_min = row['low']
        price_max = row['high']
        volume = row['volume']
        
        # Distribute volume across price bins
        for i in range(bins):
            bin_price = df['low'].min() + (i * bin_size)
            if price_min <= bin_price <= price_max:
                volume_profile[bin_price] = volume_profile.get(bin_price, 0) + volume
    
    # Find POC (Point of Control) - price with highest volume
    if volume_profile:
        poc = max(volume_profile, key=volume_profile.get)
    else:
        poc = None
    
    return {
        'profile': volume_profile,
        'poc': poc,
        'value_area_high': df['high'].max(),
        'value_area_low': df['low'].min()
    }


if __name__ == "__main__":
    # Test
    import pandas as pd
    
    # Sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='10T')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    df = pd.DataFrame({
        'close': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Test indicators
    rsi = calculate_rsi(df['close'])
    print(f"RSI: {rsi.iloc[-1]:.2f}")
    
    ema = calculate_ema(df['close'], 20)
    print(f"EMA(20): {ema.iloc[-1]:.2f}")
    
    macd, signal, hist = calculate_macd(df['close'])
    print(f"MACD: {macd.iloc[-1]:.2f}")

