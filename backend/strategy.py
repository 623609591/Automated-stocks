"""
策略层：对接国金 QMT、计算大盘环境、买卖逻辑等
当前使用 mock 数据；接入真实 QMT 时在此模块实现：
  - 连接 MiniQMT、心跳、资金/持仓/成交查询
  - 上证指数、MA20、近10日下跌天数、红黄绿灯
  - 策略参数（可从配置文件或数据库读取）
  - 资产曲线历史（可从本地文件或数据库读取）
"""
import os
from mock_data import (
    get_connection_status as _mock_connection,
    get_account_overview as _mock_account,
    get_market_env as _mock_market_env,
    get_strategy_params as _mock_params,
    get_holdings as _mock_holdings,
    get_trade_history as _mock_trades,
    get_next_schedule as _mock_schedule,
    get_candidates as _mock_candidates,
    get_equity_curve as _mock_equity,
)

# 是否使用真实 QMT（需自行实现 fetch_from_qmt 等）
USE_REAL_QMT = os.environ.get("USE_REAL_QMT", "").lower() in ("1", "true", "yes")


def get_connection_status():
    if USE_REAL_QMT:
        pass  # return fetch_connection_from_qmt()
    return _mock_connection()


def get_account_overview():
    if USE_REAL_QMT:
        pass  # return fetch_account_from_qmt()
    return _mock_account()


def get_market_env():
    if USE_REAL_QMT:
        pass  # return compute_market_env_from_qmt()
    return _mock_market_env()


def get_strategy_params():
    if USE_REAL_QMT:
        pass  # return load_strategy_params()
    return _mock_params()


def get_holdings():
    if USE_REAL_QMT:
        pass  # return fetch_holdings_from_qmt()
    return _mock_holdings()


def get_trade_history():
    if USE_REAL_QMT:
        pass  # return fetch_trades_from_qmt()
    return _mock_trades()


def get_next_schedule():
    if USE_REAL_QMT:
        pass  # return compute_next_schedule()
    return _mock_schedule()


def get_candidates():
    if USE_REAL_QMT:
        pass  # return fetch_candidates_from_qmt()
    return _mock_candidates()


def get_equity_curve():
    if USE_REAL_QMT:
        pass  # return load_equity_curve_from_storage()
    return _mock_equity()
