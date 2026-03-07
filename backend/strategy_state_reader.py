"""
从 QMT 策略写入的状态文件读取数据，供 FastAPI 暴露给监控大屏。
策略在 QMT 端运行时通过 DASHBOARD_STATE_PATH 写入同一文件，本模块读取。
"""
import os
import json

# 状态文件路径：与 QMT.py 中 DASHBOARD_STATE_PATH 指向同一文件
STATE_FILE = os.environ.get(
    "STRATEGY_STATE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy_state.json"),
)
def _read_state():
    """读取状态文件，失败或不存在返回 None"""
    if not STATE_FILE or not os.path.isfile(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def get_state():
    """
    读取状态文件。文件存在则返回 (state, updated_at)；不存在返回 (None, None)。
    不做过期判断，有文件就返回，无 mock。
    """
    state = _read_state()
    if not state:
        return None, None
    return state, state.get("updated_at")


def get_connection_status_from_state(state):
    return state.get("connection") if state else None


def get_account_overview_from_state(state):
    return state.get("account") if state else None


def get_market_env_from_state(state):
    return state.get("market_env") if state else None


def get_strategy_params_from_state(state):
    return state.get("strategy_params") if state else None


def get_holdings_from_state(state):
    return state.get("holdings") if state else None


def get_trade_history_from_state(state):
    return state.get("trades") if state else None


def get_next_schedule_from_state(state):
    return state.get("schedule") if state else None


def get_candidates_from_state(state):
    return state.get("candidates") if state else None


def get_equity_curve_from_state(state):
    return state.get("equity") if state else None
