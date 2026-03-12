"""
策略层：从 QMT 策略状态文件读取，供监控大屏展示。无 mock，无数据时返回空结构并带 updatedAt。
"""
from strategy_state_reader import (
    get_state,
    get_connection_status_from_state,
    get_account_overview_from_state,
    get_market_env_from_state,
    get_market_sentiment_from_state,
    get_holdings_from_state,
    get_trade_history_from_state,
    get_next_schedule_from_state,
    get_candidates_from_state,
    get_equity_curve_from_state,
)


def _with_updated_at(data, updated_at):
    if data is None:
        return None
    out = dict(data)
    out["updatedAt"] = updated_at
    return out


def get_state_meta():
    """返回 { updatedAt } 供前端展示上次更新时间"""
    state, updated_at = get_state()
    return {"updatedAt": updated_at}


def get_connection_status():
    state, updated_at = get_state()
    if state:
        r = get_connection_status_from_state(state)
        if r is not None:
            return _with_updated_at(r, updated_at)
    return {"connected": False, "lastHeartbeat": None, "accountId": None, "qmtHost": None, "updatedAt": None}


def get_account_overview():
    state, updated_at = get_state()
    if state:
        r = get_account_overview_from_state(state)
        if r is not None:
            return _with_updated_at(r, updated_at)
    return {"totalAsset": 0, "available": 0, "todayPnl": 0, "todayPnlRatio": 0, "dailyLossLimitHit": False, "updatedAt": None}


def get_market_env():
    state, updated_at = get_state()
    if state:
        r = get_market_env_from_state(state)
        if r is not None:
            return _with_updated_at(r, updated_at)
    return {"signal": "YELLOW", "shIndex": None, "shMa20": None, "shTodayReturn": None, "dropDaysIn10": None, "updatedAt": None}


def get_market_sentiment():
    state, updated_at = get_state()
    if state:
        r = get_market_sentiment_from_state(state)
        if r is not None:
            return _with_updated_at(r, updated_at)
    return {"label": "情绪正常", "avgChange": 0.0, "updatedAt": None}


def get_holdings():
    state, _ = get_state()
    if state:
        r = get_holdings_from_state(state)
        if r is not None:
            return r
    return []


def get_trade_history():
    state, _ = get_state()
    if state:
        r = get_trade_history_from_state(state)
        if r is not None:
            return r
    return []


def get_next_schedule():
    state, updated_at = get_state()
    if state:
        r = get_next_schedule_from_state(state)
        if r is not None:
            return _with_updated_at(r, updated_at)
    return {"now": None, "nextBuy": None, "nextSell": None, "isWeekend": None, "updatedAt": None}


def get_candidates():
    state, _ = get_state()
    if state:
        r = get_candidates_from_state(state)
        if r is not None:
            return r
    return []


def get_equity_curve():
    state, _ = get_state()
    if state:
        r = get_equity_curve_from_state(state)
        if r is not None:
            return r
    return []
