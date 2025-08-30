# Quotex API Railway Deployment Guide

## ⚠️ Important: Railway Deployment Limitations

**Railway cannot run Playwright browser automation**, which is required for real Quotex connections. You have two options:

1. **Local Deployment** (Recommended) - Full functionality with real Quotex data
2. **Railway Deployment** - Simplified API without real data (for testing only)

## Overview
This guide explains deployment options for the Quotex API service.

## Features
The API server (`api_server.py`) provides:
- **GET /candles** - Fetch historical candle data
- **POST /candles/progressive** - Get progressive candle data (main endpoint for trading bots)
- **GET /candles/realtime/{asset}** - Real-time candle streaming
- **GET /balance** - Account balance
- **GET /assets** - List all available assets
- **POST /trade** - Place trades
- **GET /profile** - User profile information
- **GET /status** - Connection status

## Deployment Steps

### Option 1: Local Deployment (RECOMMENDED)

**For production trading bots with real Quotex data:**

1. Run locally on your machine or VPS:
```bash
pip install -r requirements.txt
python api_server.py
```

2. Access at `http://localhost:8000`

3. Keep running 24/7 using:
   - Windows: Task Scheduler
   - Linux: systemd service or screen/tmux
   - VPS: PM2 or supervisor

### Option 2: Railway Deployment (Simplified Version)

**Note:** This version does NOT connect to real Quotex data due to browser automation limitations.

#### Files for Railway:
- `api_server_simple.py` - Simplified FastAPI server
- `requirements_simple.txt` - Minimal dependencies
- `Procfile` - Update to: `web: python api_server_simple.py`
- `runtime.txt` - Python version

### Deploy Simplified Version to Railway

1. **Update Procfile:**
```
web: python api_server_simple.py
```

2. **Use simplified requirements:**
```bash
cp requirements_simple.txt requirements.txt
```

3. **Push to GitHub:**
```bash
git add .
git commit -m "Use simplified version for Railway"
git push
```

4. **Deploy on Railway:**
   - Connect GitHub repo
   - Railway will auto-deploy
   - No browser dependencies needed

### 3. Access Your API

Once deployed, Railway provides a URL like:
```
https://your-app.railway.app
```

Test endpoints:
```bash
# Check status
curl https://your-app.railway.app/status

# Get candles
curl "https://your-app.railway.app/candles?asset=EURUSD_otc&period=60"

# Get progressive candles (for trading bots)
curl -X POST https://your-app.railway.app/candles/progressive \
  -H "Content-Type: application/json" \
  -d '{"asset": "EURUSD_otc", "period": 60, "days": 1}'
```

## Important Notes

### Session Management
- The API maintains persistent WebSocket connections
- Automatically reconnects on disconnection
- Session cookies are stored in `session.json`

### Why Browser Automation Doesn't Work on Railway

1. **Playwright requires headless browser** - Complex system dependencies
2. **Railway's container environment** - Limited support for browser processes
3. **Authentication cookies** - Quotex requires browser-based authentication

### Recommended Architecture

```
[Local Machine/VPS]
    |
    v
[api_server.py with Playwright]
    |
    v
[Real Quotex WebSocket Connection]
    |
    v
[Your Trading Bot accesses http://localhost:8000]
```

### Troubleshooting

**Connection Issues:**
- Check `/status` endpoint for connection state
- Review Railway logs for errors
- Ensure `config.ini` has correct credentials

**Playwright Issues:**
- Railway uses headless Chrome
- First deployment takes longer (browser installation)
- Check nixpacks.toml configuration

**WebSocket Disconnections:**
- Normal behavior, auto-reconnect is implemented
- Check connection_keeper background task

## Using the API for Trading Bots

Example Python client:
```python
import requests
import json

API_URL = "https://your-app.railway.app"

# Get progressive candles for analysis
response = requests.post(f"{API_URL}/candles/progressive", 
    json={"asset": "EURUSD_otc", "period": 60, "days": 7})
    
candles = response.json()["candles"]

# Use candles for your trading strategy
for candle in candles:
    print(f"Time: {candle['time']}, Close: {candle['close']}")
```

## Monitoring
- Railway provides logs in dashboard
- Check `/status` for uptime
- Set up health checks on `/` endpoint

## Security
- Never commit credentials to Git
- Use Railway environment variables for sensitive data
- Consider implementing API keys for production

## Support
For issues:
1. Check Railway logs
2. Test locally first: `python api_server.py`
3. Verify Playwright installation
4. Check WebSocket connection status
