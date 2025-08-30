#!/usr/bin/env python3
"""
Example usage of the Quotex API for trading bots
"""

import requests
import json
from datetime import datetime

# API base URL
API_URL = "http://localhost:8000"  # Change to your Railway URL when deployed

def get_progressive_candles(asset="EURUSD_otc", period=60, days=1):
    """
    Fetch progressive candle data - main function for trading bots
    """
    endpoint = f"{API_URL}/candles/progressive"
    
    payload = {
        "asset": asset,
        "period": period,
        "days": days,
        "offset": 3600  # Optional, defaults to 3600
    }
    
    print(f"Fetching {days} day(s) of {asset} candles with {period}s period...")
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Received {data['count']} candles")
        
        return data['candles']
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def analyze_candles(candles):
    """
    Simple analysis example for trading strategy
    """
    if not candles:
        return
    
    print("\n📊 Candle Analysis:")
    print(f"Total candles: {len(candles)}")
    
    # Get latest candles
    latest_candles = candles[-10:]  # Last 10 candles
    
    for candle in latest_candles[-3:]:  # Show last 3
        time_str = datetime.fromtimestamp(candle['time']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  Time: {time_str}")
        print(f"  Open: {candle['open']}, Close: {candle['close']}")
        print(f"  High: {candle['high']}, Low: {candle['low']}")
        print(f"  Direction: {'🟢 UP' if candle['close'] > candle['open'] else '🔴 DOWN'}")
        print()
    
    # Calculate simple trend
    recent_trend = sum(1 if c['close'] > c['open'] else -1 for c in latest_candles)
    
    if recent_trend > 3:
        print("📈 Trend: BULLISH")
    elif recent_trend < -3:
        print("📉 Trend: BEARISH")
    else:
        print("➡️ Trend: NEUTRAL")

def get_balance():
    """
    Get account balance
    """
    try:
        response = requests.get(f"{API_URL}/balance?account_type=PRACTICE")
        data = response.json()
        print(f"💰 Balance: ${data['balance']} ({data['account_type']})")
        return data['balance']
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

def check_connection():
    """
    Check API connection status
    """
    try:
        response = requests.get(f"{API_URL}/status")
        data = response.json()
        
        if data['connected']:
            print("✅ API Connected to Quotex")
            if data['uptime_seconds']:
                uptime_min = data['uptime_seconds'] / 60
                print(f"   Uptime: {uptime_min:.1f} minutes")
        else:
            print("❌ API Not Connected")
            if data['last_error']:
                print(f"   Error: {data['last_error']}")
        
        return data['connected']
    except Exception as e:
        print(f"❌ API Server not running: {e}")
        return False

def main():
    """
    Main example workflow for a trading bot
    """
    print("=" * 50)
    print("🤖 Quotex Trading Bot Example")
    print("=" * 50)
    
    # 1. Check connection
    if not check_connection():
        print("\n⚠️ Please start the API server first:")
        print("   python api_server.py")
        return
    
    print()
    
    # 2. Get balance
    balance = get_balance()
    print()
    
    # 3. Get candle data
    candles = get_progressive_candles(
        asset="EURUSD_otc",
        period=60,  # 1 minute candles
        days=1      # Last 1 day
    )
    
    # 4. Analyze candles
    if candles:
        analyze_candles(candles)
    
    print("\n" + "=" * 50)
    print("💡 Use this data for your trading strategy!")
    print("=" * 50)

if __name__ == "__main__":
    main()
