"""
国金 QMT 自动化策略 - 后端 API
提供前端监控页所需的所有接口，数据结构与 src/api/mockData.js 一致。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strategy import (
    get_connection_status,
    get_account_overview,
    get_market_env,
    get_strategy_params,
    get_holdings,
    get_trade_history,
    get_next_schedule,
    get_candidates,
    get_equity_curve,
)

app = FastAPI(title="Automated-stocks API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/connection")
def api_connection():
    return get_connection_status()


@app.get("/api/account")
def api_account():
    return get_account_overview()


@app.get("/api/market_env")
def api_market_env():
    return get_market_env()


@app.get("/api/strategy_params")
def api_strategy_params():
    return get_strategy_params()


@app.get("/api/holdings")
def api_holdings():
    return get_holdings()


@app.get("/api/trades")
def api_trades():
    return get_trade_history()


@app.get("/api/schedule")
def api_schedule():
    return get_next_schedule()


@app.get("/api/candidates")
def api_candidates():
    return get_candidates()


@app.get("/api/equity")
def api_equity():
    return get_equity_curve()


@app.get("/")
def root():
    return {"message": "Automated-stocks API", "docs": "/docs"}
