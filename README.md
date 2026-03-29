# Binance Futures Trading Bot

A Python CLI application that places Market and Limit orders on Binance Futures Demo Trading environment.

## Setup

1. Clone the repo:
   git clone https://github.com/YOUR_USERNAME/trading-bot.git
   cd trading_bot

2. Create virtual environment:
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Create a `.env` file in the root folder:
   BINANCE_API_KEY=your_key_here
   BINANCE_API_SECRET=your_secret_here

## How to Run

**Market Order:**
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

**Limit Order:**
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.1 --price 95000

## Project Structure

trading_bot/
  bot/
    __init__.py
    client.py        # API client wrapper
    orders.py        # Order placement logic
    validators.py    # Input validation
    logging_config.py
  cli.py             # CLI entry point
  .env               # API credentials (not committed)
  requirements.txt
  README.md

## Assumptions
- Uses Binance Futures Demo Trading API (demo-fapi.binance.com)
- Minimum order notional is 100 USDT
- For LIMIT orders, price must be above current market price for SELL
- Logs are saved to logs/trading_bot.log
- Price is only required for LIMIT orders