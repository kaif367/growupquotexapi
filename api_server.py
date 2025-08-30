# api_server.py

import os
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging
from quotexapi.stable_api import Quotex
from quotexapi.config import email, password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for connection management
client = None
connection_lock = asyncio.Lock()
last_connection_time = None
connection_status = {"connected": False, "last_error": None, "last_connected": None}

# Request/Response Models
class CandleRequest(BaseModel):
    asset: str = "EURUSD_otc"
    period: int = 60
    days: int = 1
    offset: Optional[int] = 3600

class TradeRequest(BaseModel):
    amount: float
    asset: str
    direction: str  # "call" or "put"
    duration: int = 60

class BalanceResponse(BaseModel):
    balance: float
    account_type: str

class ConnectionStatus(BaseModel):
    connected: bool
    last_error: Optional[str]
    last_connected: Optional[str]
    uptime_seconds: Optional[float]

# Connection manager
async def ensure_connection():
    """Ensure client is connected, reconnect if necessary"""
    global client, last_connection_time, connection_status
    
    async with connection_lock:
        if client is None:
            logger.info("Initializing Quotex client...")
            client = Quotex(
                email=email,
                password=password,
                lang="pt",
            )
            
        if not connection_status["connected"]:
            try:
                logger.info("Attempting to connect to Quotex...")
                check, reason = await client.connect()
                if check:
                    connection_status["connected"] = True
                    connection_status["last_connected"] = datetime.now().isoformat()
                    connection_status["last_error"] = None
                    last_connection_time = time.time()
                    logger.info(f"Connected successfully: {reason}")
                else:
                    connection_status["connected"] = False
                    connection_status["last_error"] = reason
                    logger.error(f"Connection failed: {reason}")
                    raise HTTPException(status_code=503, detail=f"Failed to connect: {reason}")
            except Exception as e:
                connection_status["connected"] = False
                connection_status["last_error"] = str(e)
                logger.error(f"Connection error: {e}")
                raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}")
        
        # Check if connection is still alive
        if not await client.check_connect():
            connection_status["connected"] = False
            logger.warning("Connection lost, attempting to reconnect...")
            check, reason = await client.connect()
            if check:
                connection_status["connected"] = True
                connection_status["last_connected"] = datetime.now().isoformat()
                last_connection_time = time.time()
                logger.info("Reconnected successfully")
            else:
                connection_status["last_error"] = reason
                raise HTTPException(status_code=503, detail=f"Reconnection failed: {reason}")

# Background task to maintain connection
async def connection_keeper():
    """Keep connection alive by sending periodic pings"""
    while True:
        try:
            if connection_status["connected"]:
                if client and await client.check_connect():
                    logger.debug("Connection is alive")
                else:
                    logger.warning("Connection check failed, will reconnect on next request")
                    connection_status["connected"] = False
        except Exception as e:
            logger.error(f"Connection keeper error: {e}")
            connection_status["connected"] = False
        
        await asyncio.sleep(30)  # Check every 30 seconds

# Lifespan manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting API server...")
    # Start background connection keeper
    asyncio.create_task(connection_keeper())
    
    # Try initial connection
    try:
        await ensure_connection()
    except Exception as e:
        logger.warning(f"Initial connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")
    if client:
        client.close()

# Initialize FastAPI app
app = FastAPI(
    title="Quotex API Service",
    description="API service for Quotex trading data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Quotex API",
        "version": "1.0.0",
        "connected": connection_status["connected"]
    }

@app.get("/status", response_model=ConnectionStatus)
async def get_status():
    """Get connection status"""
    uptime = None
    if last_connection_time:
        uptime = time.time() - last_connection_time
    
    return ConnectionStatus(
        connected=connection_status["connected"],
        last_error=connection_status["last_error"],
        last_connected=connection_status["last_connected"],
        uptime_seconds=uptime
    )

@app.post("/connect")
async def connect():
    """Manually trigger connection"""
    await ensure_connection()
    return {"status": "connected", "message": "Successfully connected to Quotex"}

@app.get("/profile")
async def get_profile():
    """Get user profile information"""
    await ensure_connection()
    try:
        profile = await client.get_profile()
        return {
            "nick_name": profile.nick_name,
            "profile_id": profile.profile_id,
            "demo_balance": profile.demo_balance,
            "live_balance": profile.live_balance,
            "currency": profile.currency_code,
            "country": profile.country_name
        }
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/balance", response_model=BalanceResponse)
async def get_balance(account_type: str = Query("PRACTICE", enum=["PRACTICE", "REAL"])):
    """Get account balance"""
    await ensure_connection()
    try:
        client.change_account(account_type)
        balance = await client.get_balance()
        return BalanceResponse(balance=balance, account_type=account_type)
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candles")
async def get_candles(
    asset: str = Query("EURUSD_otc", description="Asset symbol"),
    period: int = Query(60, description="Period in seconds"),
    offset: int = Query(3600, description="Offset in seconds"),
    end_time: Optional[float] = Query(None, description="End time timestamp")
):
    """Get historical candles"""
    await ensure_connection()
    try:
        if end_time is None:
            end_time = time.time()
        
        candles = await client.get_candles(asset, end_time, offset, period)
        return {
            "asset": asset,
            "period": period,
            "count": len(candles) if candles else 0,
            "candles": candles
        }
    except Exception as e:
        logger.error(f"Error getting candles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candles/progressive")
async def get_candles_progressive_info():
    """GET endpoint to show usage information"""
    return {
        "message": "This endpoint requires a POST request",
        "method": "POST",
        "url": "/candles/progressive",
        "example_request": {
            "asset": "EURUSD_otc",
            "period": 60,
            "days": 1,
            "offset": 3600
        },
        "description": "Fetches progressive historical candle data for trading bots"
    }

@app.post("/candles/progressive")
async def get_candles_progressive(request: CandleRequest):
    """Get progressive historical candles (similar to get_candle_progressive)"""
    await ensure_connection()
    try:
        from quotexapi.expiration import get_timestamp_days_ago, timestamp_to_date
        
        list_candles = []
        size = request.days * 24
        timestamp = get_timestamp_days_ago(request.days)
        end_from_time = (int(timestamp) - int(timestamp) % request.period) + request.offset
        
        logger.info(f"Fetching {size} hours of data for {request.asset}")
        
        for i in range(size):
            candles = await client.get_candles(
                request.asset, 
                end_from_time, 
                request.offset, 
                request.period, 
                progressive=True
            )
            if candles:
                list_candles += candles
            if i >= size:
                request.offset *= 2
            end_from_time = end_from_time + request.offset
            
            # Add small delay to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        # Remove duplicates
        unique_candles = list({frozenset(d.items()): d for d in list_candles}.values())
        
        return {
            "asset": request.asset,
            "period": request.period,
            "days": request.days,
            "count": len(unique_candles),
            "candles": unique_candles
        }
    except Exception as e:
        logger.error(f"Error getting progressive candles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candles/realtime/{asset}")
async def get_realtime_candles(
    asset: str,
    period: int = Query(60, description="Period in seconds")
):
    """Get realtime candles for an asset"""
    await ensure_connection()
    try:
        client.start_candles_stream(asset, period)
        await asyncio.sleep(2)  # Wait for data to arrive
        
        candles = await client.get_realtime_candles(asset, period)
        return {
            "asset": asset,
            "period": period,
            "candles": candles,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting realtime candles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets")
async def get_assets():
    """Get all available assets"""
    await ensure_connection()
    try:
        all_assets = await client.get_all_assets()
        asset_names = client.get_all_asset_name()
        
        return {
            "count": len(all_assets),
            "assets": all_assets,
            "asset_names": asset_names
        }
    except Exception as e:
        logger.error(f"Error getting assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets/{asset}/status")
async def check_asset_status(asset: str):
    """Check if an asset is open for trading"""
    await ensure_connection()
    try:
        asset_name, asset_data = await client.get_available_asset(asset, force_open=False)
        if asset_data:
            return {
                "asset": asset_name,
                "is_open": asset_data[2],
                "data": asset_data
            }
        else:
            return {
                "asset": asset,
                "is_open": False,
                "message": "Asset not found"
            }
    except Exception as e:
        logger.error(f"Error checking asset status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trade")
async def place_trade(request: TradeRequest):
    """Place a trade (buy option)"""
    await ensure_connection()
    try:
        status, buy_info = await client.buy(
            request.amount,
            request.asset,
            request.direction,
            request.duration
        )
        
        if status:
            return {
                "status": "success",
                "trade_id": buy_info.get("id"),
                "details": buy_info
            }
        else:
            raise HTTPException(status_code=400, detail="Trade failed")
    except Exception as e:
        logger.error(f"Error placing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/{asset}")
async def get_payment_info(asset: str):
    """Get payment/payout information for an asset"""
    await ensure_connection()
    try:
        payment_data = client.get_payment()
        if asset in payment_data:
            return payment_data[asset]
        else:
            raise HTTPException(status_code=404, detail=f"Asset {asset} not found")
    except Exception as e:
        logger.error(f"Error getting payment info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals")
async def get_signals():
    """Get trading signals"""
    await ensure_connection()
    try:
        client.start_signals_data()
        await asyncio.sleep(2)  # Wait for signals
        signals = client.get_signal_data()
        return {
            "count": len(signals),
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
