# Short/Long Trading System

سیستم معاملاتی خودکار برای اسکالپینگ در تایم فریم 10 دقیقه با استراتژی‌های Short و Long

## 📋 فهرست مطالب

- [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
- [ساختار پروژه](#ساختار-پروژه)
- [استراتژی‌ها](#استراتژی‌ها)
- [استفاده](#استفاده)
- [مستندات](#مستندات)

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8+
- pip

### نصب

```bash
# کلون کردن ریپازیتوری
git clone <repository-url>
cd Short_Long

# نصب کتابخانه‌ها
pip install -r requirements.txt
```

## 📁 ساختار پروژه

```
Short_Long/
├── data/                  # داده‌های بازار
├── strategies/           # استراتژی‌های معاملاتی
│   ├── base_strategy.py
│   ├── volume_breakout.py
│   ├── rsi_divergence.py
│   ├── bollinger_squeeze.py
│   └── ema_crossover.py
├── indicators/           # اندیکاتورهای تکنیکال
│   └── technical_indicators.py
├── backtesting/          # ماژول بک‌تست
├── utils/                # ابزارهای کمکی
├── logs/                 # فایل‌های لاگ
├── results/              # نتایج معاملات
├── Research/             # تحقیقات و استراتژی‌ها
├── config.py             # تنظیمات سیستم
├── data_loader.py         # ماژول دریافت داده
└── requirements.txt      # وابستگی‌ها
```

## 📈 استراتژی‌ها

این سیستم شامل 4 استراتژی اصلی است:

### 1. Volume Confirmed Breakout
**شکست با تایید حجم**
- ورود در شکست سطوح مقاومت/حمایت با حجم حداقل 2-3 برابر میانگین
- فیلتر سیگنال‌های کاذب
- مناسب برای بازارهای رونددار

### 2. RSI Divergence
**واگرایی RSI با سطوح کلیدی**
- تشخیص واگرایی صعودی/نزولی
- ورود در سطوح بیش‌خرید/بیش‌فروش
- نسبت ریسک/پاداش 1:3

### 3. Bollinger Squeeze Breakout
**شکست از باندهای بولینجر فشرده**
- شناسایی دوره‌های آرامش قبل از حرکت بزرگ
- تایید با MACD
- مناسب برای نوسانات انفجاری

### 4. EMA Crossover
**کراس EMA با تایید حجم**
- کراس EMA سریع و کند
- تایید با حجم بالا
- مناسب برای روندهای قوی

## 💻 استفاده

### دریافت داده‌های بازار

```python
from data_loader import DataLoader

# ایجاد loader
loader = DataLoader(exchange_name="binance")

# دریافت قیمت لحظه‌ای
ticker = loader.get_ticker("SOL/USDT")
print(f"قیمت: ${ticker['price']:.2f}")

# دریافت داده‌های تاریخی
df = loader.get_ohlcv("SOL/USDT", timeframe="10m", days=30)
```

### استفاده از اندیکاتورها

```python
from indicators.technical_indicators import calculate_rsi, calculate_ema

# محاسبه RSI
rsi = calculate_rsi(df['close'], period=14)

# محاسبه EMA
ema = calculate_ema(df['close'], period=20)
```

### استفاده از استراتژی‌ها

```python
from strategies.volume_breakout import VolumeBreakoutStrategy

# ایجاد استراتژی
strategy = VolumeBreakoutStrategy(volume_multiplier=2.0)

# تولید سیگنال
signal = strategy.generate_signal(df)

if signal:
    print(f"سیگنال: {signal['signal']}")
    print(f"ورود: ${signal['entry_price']:.2f}")
    print(f"حد ضرر: ${signal['stop_loss']:.2f}")
    print(f"حد سود: ${signal['take_profit']:.2f}")
```

## ⚙️ تنظیمات

تنظیمات در فایل `config.py`:

```python
# جفت ارزها
TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# تایم فریم
TIMEFRAME = "10m"

# مدیریت ریسک
RISK_CONFIG = {
    "max_position_size": 0.02,  # 2% سرمایه در هر معامله
    "risk_reward_ratio": 2.0,   # نسبت ریسک به پاداش
}
```

## 📚 مستندات

- [راهنمای دریافت داده‌های لحظه‌ای](./راهنمای_دریافت_اطلاعات_لحظه_ای_ارزها.txt)
- [تحقیقات استراتژی‌ها](./Research/)

## 🔧 توسعه

برای افزودن استراتژی جدید:

1. کلاس جدید از `BaseStrategy` ارث‌بری کنید
2. متدهای `generate_signal`, `calculate_stop_loss`, `calculate_take_profit` را پیاده‌سازی کنید
3. استراتژی را در `strategies/__init__.py` اضافه کنید

## ⚠️ هشدار

**این سیستم فقط برای اهداف آموزشی است.**
- همیشه قبل از معامله با سرمایه واقعی، بک‌تست کامل انجام دهید
- از سرمایه‌ای استفاده کنید که از دست دادنش مشکلی ایجاد نکند
- مدیریت ریسک را جدی بگیرید

## 📝 لایسنس

این پروژه برای استفاده شخصی است.

## 🤝 مشارکت

برای پیشنهادات و باگ‌ها، لطفاً Issue ایجاد کنید.

---

**موفق باشید! 📈**
