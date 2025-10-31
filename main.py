"""
Main Entry Point
نقطه ورود اصلی برنامه
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
from data_loader import DataLoader
from strategies.volume_breakout import VolumeBreakoutStrategy
from strategies.rsi_divergence import RSIDivergenceStrategy
from strategies.bollinger_squeeze import BollingerSqueezeStrategy
from strategies.ema_crossover import EMACrossoverStrategy
import config

# Ensure logs directory exists
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_CONFIG.get('level', 'INFO'), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / config.LOG_CONFIG.get('file', 'trading.log')),
        logging.StreamHandler() if config.LOG_CONFIG.get('console', True) else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


def test_data_loader(symbol: str = "SOL/USDT") -> Optional:
    """
    تست دریافت داده
    
    Args:
        symbol: نماد معاملاتی برای تست
        
    Returns:
        DataFrame با داده‌های OHLCV یا None در صورت خطا
    """
    print("\n" + "="*60)
    print("Testing Data Loader...")
    print("="*60)
    
    try:
        loader = DataLoader(exchange_name=config.EXCHANGE)
        
        # Test ticker
        print(f"\n1. Testing ticker fetch for {symbol}...")
        ticker = loader.get_ticker(symbol)
        if ticker:
            print(f"   ✓ SOL/USDT Price: ${ticker['price']:.2f}")
            print(f"   ✓ 24h High: ${ticker['high_24h']:.2f}")
            print(f"   ✓ 24h Low: ${ticker['low_24h']:.2f}")
            print(f"   ✓ 24h Volume: ${ticker['volume_24h']:,.2f}")
        else:
            print("   ✗ Failed to fetch ticker")
            return None
        
        # Test historical data
        print(f"\n2. Testing historical data fetch...")
        df = loader.get_ohlcv(symbol, timeframe=config.TIMEFRAME, days=7)
        if not df.empty:
            print(f"   ✓ Fetched {len(df)} candles")
            print(f"   ✓ Date range: {df.index[0]} to {df.index[-1]}")
            print(f"   ✓ Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        else:
            print("   ✗ Failed to fetch historical data")
            return None
        
        return df
        
    except Exception as e:
        logger.error(f"Error in data loader test: {e}", exc_info=True)
        print(f"   ✗ Error: {e}")
        return None


def test_strategies(df) -> None:
    """
    تست استراتژی‌ها
    
    Args:
        df: DataFrame با داده‌های OHLCV
    """
    if df is None or df.empty:
        print("\n⚠ Cannot test strategies - no data available")
        return
    
    if len(df) < 50:
        print(f"\n⚠ Warning: Limited data ({len(df)} candles). Some strategies may not work properly.")
    
    print("\n" + "="*60)
    print("Testing Strategies...")
    print("="*60)
    
    strategies = [
        ("Volume Breakout", VolumeBreakoutStrategy(
            volume_multiplier=config.STRATEGY_CONFIG.get('volume_multiplier', 2.0)
        )),
        ("RSI Divergence", RSIDivergenceStrategy(
            rsi_period=config.STRATEGY_CONFIG.get('rsi_period', 14),
            rsi_oversold=config.STRATEGY_CONFIG.get('rsi_oversold', 30),
            rsi_overbought=config.STRATEGY_CONFIG.get('rsi_overbought', 70)
        )),
        ("Bollinger Squeeze", BollingerSqueezeStrategy(
            bb_period=config.STRATEGY_CONFIG.get('bb_period', 20),
            bb_std=config.STRATEGY_CONFIG.get('bb_std', 2.0),
            atr_period=config.STRATEGY_CONFIG.get('atr_period', 14)
        )),
        ("EMA Crossover", EMACrossoverStrategy(
            fast_period=config.STRATEGY_CONFIG.get('ema_fast', 5),
            slow_period=config.STRATEGY_CONFIG.get('ema_slow', 20)
        )),
    ]
    
    signals_found = 0
    for name, strategy in strategies:
        print(f"\n{name}:")
        try:
            signal = strategy.generate_signal(df.copy())
            if signal:
                signals_found += 1
                signal_type = signal['signal'].upper()
                emoji = "🟢" if signal_type == "LONG" else "🔴"
                print(f"   {emoji} Signal: {signal_type}")
                print(f"   💵 Entry: ${signal['entry_price']:.4f}")
                print(f"   🛑 Stop Loss: ${signal['stop_loss']:.4f}")
                print(f"   🎯 Take Profit: ${signal['take_profit']:.4f}")
                print(f"   📊 Confidence: {signal['confidence']:.1%}")
                
                # Calculate risk/reward ratio
                risk = abs(signal['entry_price'] - signal['stop_loss'])
                reward = abs(signal['take_profit'] - signal['entry_price'])
                rr_ratio = reward / risk if risk > 0 else 0
                print(f"   ⚖️  Risk/Reward: 1:{rr_ratio:.2f}")
                
                # Show additional info if available
                if 'volume_ratio' in signal:
                    print(f"   📈 Volume Ratio: {signal['volume_ratio']:.2f}x")
                if 'rsi' in signal:
                    print(f"   📉 RSI: {signal['rsi']:.2f}")
            else:
                print("   ⚪ No signal generated")
        except Exception as e:
            logger.error(f"Error testing {name}: {e}", exc_info=True)
            print(f"   ✗ Error: {e}")
    
    print(f"\n📊 Summary: {signals_found}/{len(strategies)} strategies generated signals")


def main():
    """تابع اصلی"""
    print("\n" + "="*60)
    print("🚀 Short/Long Trading System - Test Run")
    print("="*60)
    print(f"📅 Exchange: {config.EXCHANGE.upper()}")
    print(f"⏱️  Timeframe: {config.TIMEFRAME}")
    print(f"📊 Trading Pairs: {', '.join(config.TRADING_PAIRS)}")
    
    try:
        # Test data loader
        test_symbol = config.TRADING_PAIRS[0] if config.TRADING_PAIRS else "SOL/USDT"
        df = test_data_loader(test_symbol)
        
        # Test strategies if we have data
        if df is not None and not df.empty:
            test_strategies(df)
        else:
            print("\n⚠ Cannot proceed with strategy testing due to data loading failure")
    
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("="*60)


if __name__ == "__main__":
    main()

