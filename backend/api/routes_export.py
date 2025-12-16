"""Export API routes for QuantStream RTQAE."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import csv
import io

from api.server import get_app_state
from core.logger import get_logger

logger = get_logger("api.routes_export")

router = APIRouter()


@router.get("/ticks")
async def export_ticks(symbol: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, limit: int = 1000, format: str = "json"):
    state = get_app_state()
    db_client = state.get('db_client')

    if not db_client:
        raise HTTPException(status_code=500, detail="Database client not initialized")

    ticks = db_client.query_ticks(symbol, start_time, end_time, limit)

    if format == "csv":
        output = io.StringIO()
        if ticks:
            writer = csv.DictWriter(output, fieldnames=ticks[0].keys())
            writer.writeheader()
            writer.writerows(ticks)
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=ticks.csv"})
    else:
        return {"ticks": ticks, "count": len(ticks)}


@router.get("/ohlcv")
async def export_ohlcv(symbol: str, timeframe: str = "1min", start_time: Optional[str] = None, end_time: Optional[str] = None, limit: int = 500, format: str = "json"):
    state = get_app_state()
    db_client = state.get('db_client')

    if not db_client:
        raise HTTPException(status_code=500, detail="Database client not initialized")

    ohlcv = db_client.query_ohlcv(symbol, timeframe, start_time, end_time, limit)

    if format == "csv":
        output = io.StringIO()
        if ohlcv:
            writer = csv.DictWriter(output, fieldnames=ohlcv[0].keys())
            writer.writeheader()
            writer.writerows(ohlcv)
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=ohlcv_{symbol}.csv"})
    else:
        return {"ohlcv": ohlcv, "count": len(ohlcv), "symbol": symbol, "timeframe": timeframe}


@router.get("/alerts")
async def export_alerts(symbol: Optional[str] = None, severity: Optional[str] = None, limit: int = 100, format: str = "json"):
    state = get_app_state()
    db_client = state.get('db_client')

    if not db_client:
        raise HTTPException(status_code=500, detail="Database client not initialized")

    alerts = db_client.query_alerts(symbol, severity, limit=limit)

    if format == "csv":
        output = io.StringIO()
        if alerts:
            writer = csv.DictWriter(output, fieldnames=alerts[0].keys())
            writer.writeheader()
            writer.writerows(alerts)
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=alerts.csv"})
    else:
        return {"alerts": alerts, "count": len(alerts)}


@router.get("/database/stats")
async def get_database_stats():
    state = get_app_state()
    db_client = state.get('db_client')

    if not db_client:
        raise HTTPException(status_code=500, detail="Database client not initialized")

    stats = db_client.get_stats()
    return {"database_stats": stats, "total_records": sum(stats.values())}
