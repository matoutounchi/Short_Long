"""
Data Loader Module
ماژول دریافت داده‌های بازار از صرافی
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """کلاس برای دریافت داده‌های بازار از صرافی‌ها"""
    
    def __init__(self, exchange_name: str = "binance"):
        """
        Initialize data loader
        
        Args:
            exchange_name: نام صرافی (binance, coinbase, etc.)
        
        Raises:
            AttributeError: اگر صرافی مورد نظر وجود نداشته باشد
        """
        self.exchange_name = exchange_name
        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            logger.info(f"Connected to {exchange_name}")
        except AttributeError:
            logger.error(f"Exchange {exchange_name} not found in ccxt")
            raise ValueError(f"Exchange '{exchange_name}' is not supported. Available exchanges: {', '.join(ccxt.exchanges)}")
    
    def get_ticker(self, symbol: str) -> dict:
        """
        دریافت اطلاعات لحظه‌ای یک ارز
        
        Args:
            symbol: نماد معاملاتی (مثل SOL/USDT)
            
        Returns:
            Dictionary containing ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume_24h': ticker['quoteVolume'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def get_ohlcv(self, symbol: str, timeframe: str = "10m", 
                   days: int = 30, limit: int = 1000) -> pd.DataFrame:
        """
        دریافت داده‌های تاریخی OHLCV
        
        Args:
            symbol: نماد معاملاتی
            timeframe: تایم فریم (1m, 5m, 10m, 1h, etc.)
            days: تعداد روزهای تاریخی
            limit: حداکثر تعداد کندل در هر درخواست
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            since = int(start_time.timestamp() * 1000)
            
            all_candles = []
            current_since = since
            batch = 0
            
            logger.info(f"Fetching {days} days of {timeframe} data for {symbol}...")
            
            while True:
                try:
                    candles = self.exchange.fetch_ohlcv(
                        symbol,
                        timeframe=timeframe,
                        since=current_since,
                        limit=limit
                    )
                    
                    if not candles:
                        break
                    
                    all_candles.extend(candles)
                    batch += 1
                    
                    last_timestamp = candles[-1][0]
                    if last_timestamp >= int(end_time.timestamp() * 1000):
                        break
                    
                    current_since = last_timestamp + 1
                    time.sleep(0.5)  # Rate limit protection
                    
                    # Prevent infinite loop
                    if batch > 100:
                        logger.warning(f"Reached maximum batch limit (100) for {symbol}")
                        break
                    
                except Exception as e:
                    logger.error(f"Error in batch {batch}: {e}")
                    if batch == 1:  # If first batch fails, retry once
                        time.sleep(2)
                        continue
                    time.sleep(5)
                    break  # Stop on repeated errors
            
            # Convert to DataFrame
            df = pd.DataFrame(
                all_candles,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            logger.info(f"Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> dict:
        """
        دریافت Order Book
        
        Args:
            symbol: نماد معاملاتی
            limit: تعداد سفارشات در هر طرف
            
        Returns:
            Dictionary with bids and asks
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return None
    
    def calculate_ofi(self, ticker: dict) -> float:
        """
        محاسبه Order Flow Imbalance
        
        Args:
            ticker: داده ticker
            
        Returns:
            OFI value
        """
        bid_volume = ticker.get('bidVolume', 0)
        ask_volume = ticker.get('askVolume', 0)
        return bid_volume - ask_volume
    
    def calculate_spread(self, ticker: dict) -> float:
        """
        محاسبه Spread
        
        Args:
            ticker: داده ticker
            
        Returns:
            Spread percentage
        """
        if ticker.get('ask') and ticker.get('bid'):
            spread = (ticker['ask'] - ticker['bid']) / ticker['last']
            return spread
        return 0.0


if __name__ == "__main__":
    # Test
    loader = DataLoader()
    
    # Get ticker
    ticker = loader.get_ticker("SOL/USDT")
    print(f"SOL/USDT Price: ${ticker['price']:.2f}")
    
    # Get historical data
    df = loader.get_ohlcv("SOL/USDT", timeframe="10m", days=7)
    print(f"\nData shape: {df.shape}")
    print(df.head())

