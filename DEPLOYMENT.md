# Quotex API Railway Deployment Guide

## Overview
This guide explains how to deploy the Quotex API service on Railway for 24/7 operation.

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

### 1. Prepare Your Repository
Ensure these files are in your repository:
- `api_server.py` - FastAPI server
- `requirements.txt` - Python dependencies
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration
- `Procfile` - Start command
- `settings/config.ini` - Your Quotex credentials

### 2. Deploy to Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Configure Environment Variables**
   In Railway dashboard, add these variables:
   ```
   PORT=8000
   PYTHON_VERSION=3.11
   PLAYWRIGHT_BROWSERS_PATH=/app/browsers
   ```

4. **Deploy**
   - Railway will automatically deploy when you push to GitHub
   - First deployment may take 5-10 minutes (installing Playwright)

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

### Railway Limitations
- Free tier: 500 hours/month
- Hobby tier ($5/month): Unlimited hours
- Memory: 512MB (free) / 8GB (hobby)

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
