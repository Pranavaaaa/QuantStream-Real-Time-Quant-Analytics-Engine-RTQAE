"""Ingestion API routes for QuantStream RTQAE."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from api.server import get_app_state
from core.logger import get_logger

logger = get_logger("api.routes_ingestion")

router = APIRouter()


class StartIngestionRequest(BaseModel):
    symbols: List[str]


@router.post("/start")
async def start_ingestion(request: StartIngestionRequest):
    state = get_app_state()
    ws_client = state.get('ws_client')

    if not ws_client:
        raise HTTPException(status_code=500, detail="WebSocket client not initialized")

    if ws_client.running:
        return {"status": "already_running", "symbols": ws_client.symbols}

    ws_client.symbols = [s.lower().strip() for s in request.symbols]
    ws_client.start()

    logger.info(f"Started ingestion for: {request.symbols}")
    return {"status": "started", "symbols": request.symbols}


@router.post("/stop")
async def stop_ingestion():
    state = get_app_state()
    ws_client = state.get('ws_client')

    if not ws_client:
        raise HTTPException(status_code=500, detail="WebSocket client not initialized")

    if not ws_client.running:
        return {"status": "not_running"}

    ws_client.stop()
    return {"status": "stopped"}


@router.get("/status")
async def get_ingestion_status():
    state = get_app_state()
    ws_client = state.get('ws_client')
    buffer = state.get('buffer')

    if not ws_client:
        raise HTTPException(status_code=500, detail="WebSocket client not initialized")

    status = {
        "running": ws_client.running,
        "symbols": ws_client.symbols,
        "connected_symbols": ws_client.get_connected_symbols(),
        "tick_count": ws_client.get_tick_count()
    }

    if buffer:
        status["buffer_stats"] = buffer.get_stats()

    return status


@router.get("/buffer")
async def get_buffer_contents(symbol: Optional[str] = None, limit: int = 100):
    state = get_app_state()
    buffer = state.get('buffer')

    if not buffer:
        raise HTTPException(status_code=500, detail="Buffer not initialized")

    if symbol:
        ticks = buffer.get_recent(symbol, limit)
        return {"symbol": symbol, "count": len(ticks), "ticks": [t.dict() for t in ticks]}
    else:
        symbols = buffer.get_all_symbols()
        return {"symbols": symbols, "data": {s: [t.dict() for t in buffer.get_recent(s, limit)] for s in symbols}}


@router.get("/latest_prices")
async def get_latest_prices():
    state = get_app_state()
    buffer = state.get('buffer')

    if not buffer:
        raise HTTPException(status_code=500, detail="Buffer not initialized")

    symbols = buffer.get_all_symbols()
    prices = {s: buffer.get_latest_price(s) for s in symbols if buffer.get_latest_price(s)}

    return {"prices": prices, "count": len(prices)}
