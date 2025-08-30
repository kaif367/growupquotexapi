#!/usr/bin/env python3
"""Test script for Quotex API endpoints"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing Quotex API Endpoints\n" + "="*40)
    
    # 1. Test status
    print("\n1. Testing /status endpoint:")
    try:
        response = requests.get(f"{API_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Test root endpoint
    print("\n2. Testing / (root) endpoint:")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Test balance
    print("\n3. Testing /balance endpoint:")
    try:
        response = requests.get(f"{API_URL}/balance?account_type=PRACTICE")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Test assets
    print("\n4. Testing /assets endpoint:")
    try:
        response = requests.get(f"{API_URL}/assets")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total assets: {data.get('count', 0)}")
        if data.get('asset_names'):
            print(f"Sample assets: {data['asset_names'][:5]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Test candles (simple)
    print("\n5. Testing /candles endpoint:")
    try:
        params = {
            "asset": "EURUSD_otc",
            "period": 60,
            "offset": 3600
        }
        response = requests.get(f"{API_URL}/candles", params=params)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Candles count: {data.get('count', 0)}")
        if data.get('candles') and len(data['candles']) > 0:
            print(f"First candle: {data['candles'][0]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Test progressive candles (main endpoint for bots)
    print("\n6. Testing /candles/progressive endpoint (main for trading bots):")
    try:
        payload = {
            "asset": "EURUSD_otc",
            "period": 60,
            "days": 1,
            "offset": 3600
        }
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{API_URL}/candles/progressive", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response summary:")
            print(f"  - Asset: {data.get('asset')}")
            print(f"  - Period: {data.get('period')} seconds")
            print(f"  - Days: {data.get('days')}")
            print(f"  - Total candles: {data.get('count', 0)}")
            
            if data.get('candles') and len(data['candles']) > 0:
                print(f"\nFirst candle:")
                print(json.dumps(data['candles'][0], indent=2))
                print(f"\nLast candle:")
                print(json.dumps(data['candles'][-1], indent=2))
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Test profile
    print("\n7. Testing /profile endpoint:")
    try:
        response = requests.get(f"{API_URL}/profile")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Profile:")
            print(f"  - Nick: {data.get('nick_name')}")
            print(f"  - Demo Balance: {data.get('demo_balance')}")
            print(f"  - Live Balance: {data.get('live_balance')}")
            print(f"  - Currency: {data.get('currency')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Make sure the API server is running (python api_server.py)")
    print("Testing in 2 seconds...\n")
    time.sleep(2)
    test_endpoints()
    print("\n" + "="*40)
    print("Testing complete!")
