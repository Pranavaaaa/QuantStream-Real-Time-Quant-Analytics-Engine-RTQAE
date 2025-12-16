"""Analytics API routes for QuantStream RTQAE."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from api.server import get_app_state
from core.logger import get_logger

logger = get_logger("api.routes_analytics")

router = APIRouter()


@router.get("/stats/{symbol}")
async def get_stats(symbol: str):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    stats = analytics_engine.get_stats(symbol.upper())
    if not stats:
        raise HTTPException(status_code=404, detail=f"No statistics for {symbol}")
    return stats


@router.get("/stats")
async def get_all_stats():
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    return analytics_engine.get_all_stats()


@router.get("/zscore/{symbol}")
async def get_zscore(symbol: str):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    zscore = analytics_engine.get_zscore(symbol.upper())
    if not zscore:
        raise HTTPException(status_code=404, detail=f"No z-score for {symbol}")
    return zscore


@router.get("/zscores")
async def get_all_zscores():
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    return analytics_engine.get_all_zscores()


@router.get("/correlation")
async def get_correlations(symbol1: Optional[str] = None, symbol2: Optional[str] = None, corr_type: str = "pearson"):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    if symbol1 and symbol2:
        corr = analytics_engine.get_correlation(symbol1.upper(), symbol2.upper(), corr_type)
        if not corr:
            raise HTTPException(status_code=404, detail=f"No correlation for {symbol1}/{symbol2}")
        return corr
    else:
        return {"correlations": analytics_engine.get_all_correlations(corr_type)}


@router.get("/correlation/matrix")
async def get_correlation_matrix():
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    matrix = analytics_engine.get_correlation_matrix()
    symbols = analytics_engine.correlation_calc.get_symbols()

    return {"symbols": symbols, "matrix": matrix.tolist() if matrix is not None else []}


@router.get("/spread")
async def get_spread(symbol1: str, symbol2: str, hedge_ratio: float = 1.0):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    spread = analytics_engine.get_spread(symbol1.upper(), symbol2.upper(), hedge_ratio)
    if not spread:
        raise HTTPException(status_code=404, detail=f"No spread data for {symbol1}/{symbol2}")
    return spread


@router.get("/regression")
async def get_regression(symbol_x: str, symbol_y: str):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    regression = analytics_engine.get_regression(symbol_x.upper(), symbol_y.upper())
    if not regression:
        raise HTTPException(status_code=404, detail=f"No regression data for {symbol_x}/{symbol_y}")
    return regression


@router.get("/adf/{symbol}")
async def get_adf_test(symbol: str):
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    adf = analytics_engine.get_adf_test(symbol.upper())
    if not adf:
        raise HTTPException(status_code=404, detail=f"No ADF test for {symbol}")
    return adf


@router.get("/summary")
async def get_analytics_summary():
    state = get_app_state()
    analytics_engine = state.get('analytics_engine')

    if not analytics_engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")

    return analytics_engine.get_summary()


@router.get("/alerts")
async def get_recent_alerts(limit: int = 20):
    state = get_app_state()
    alert_engine = state.get('alert_engine')

    if not alert_engine:
        raise HTTPException(status_code=500, detail="Alert engine not initialized")

    alerts = alert_engine.get_recent_alerts(limit)
    return {"alerts": alerts, "count": len(alerts), "total_alerts": alert_engine.get_alert_count()}
