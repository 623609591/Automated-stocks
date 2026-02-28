"""
模拟数据 - 与前端 mockData.js 结构一致
对接 QMT 时在 strategy.py 中替换为真实逻辑
"""
from datetime import datetime, timedelta


def get_connection_status():
    return {
        "connected": True,
        "lastHeartbeat": datetime.utcnow().isoformat() + "Z",
        "accountId": "****1234",
        "qmtHost": "127.0.0.1:55666",
    }


def get_account_overview():
    return {
        "totalAsset": 128560,
        "available": 51200,
        "todayPnl": 1260,
        "todayPnlRatio": 0.99,
        "dailyLossLimitHit": False,
    }


def get_market_env():
    return {
        "signal": "GREEN",  # RED | YELLOW | GREEN
        "shIndex": 3245.67,
        "shMa20": 3210.22,
        "shTodayReturn": 0.85,
        "dropDaysIn10": 1,
    }


def get_strategy_params():
    return {
        "maxPositionGreen": 0.6,
        "maxPositionYellow": 0.4,
        "maxStocks": 3,
        "minBuyVolume": 100,
        "maxDailyLossRatio": 0.02,
        "buyTime": "14:50",
        "sellStart": "09:30",
        "sellEnd": "09:59",
        "takeProfit": 3.0,
        "stopLoss": -1.5,
        "minPrice": 8,
        "maxPrice": 40,
        "minRise": 1.5,
        "maxRise": 4.5,
    }


def get_holdings():
    return [
        {"code": "600519.SH", "name": "贵州茅台", "volume": 100, "costPrice": 1680, "currentPrice": 1720.5, "pnlRatio": 2.41},
        {"code": "000858.SZ", "name": "五粮液", "volume": 200, "costPrice": 145.2, "currentPrice": 148.8, "pnlRatio": 2.48},
        {"code": "300750.SZ", "name": "宁德时代", "volume": 100, "costPrice": 198.5, "currentPrice": 195.2, "pnlRatio": -1.66},
    ]


def get_trade_history():
    now = datetime.utcnow()
    return [
        {"time": (now - timedelta(hours=1)).isoformat() + "Z", "code": "600519.SH", "name": "贵州茅台", "side": "buy", "volume": 100, "price": 1680, "reason": "自动买入"},
        {"time": (now - timedelta(days=2)).isoformat() + "Z", "code": "000001.SZ", "name": "平安银行", "side": "sell", "volume": 200, "price": 12.35, "reason": "止盈"},
        {"time": (now - timedelta(days=3)).isoformat() + "Z", "code": "002594.SZ", "name": "比亚迪", "side": "sell", "volume": 100, "price": 245.6, "reason": "止损"},
    ]


def get_next_schedule():
    now = datetime.now()
    wd = now.weekday()  # 0=Monday, 6=Sunday
    return {
        "now": now.strftime("%Y-%m-%d %H:%M:%S"),
        "nextBuy": "今日 14:50",
        "nextSell": "明日 09:30 - 09:59",
        "isWeekend": wd >= 5,
    }


def get_candidates():
    return [
        {"code": "600519.SH", "name": "贵州茅台", "price": 1720.5, "rise": 2.1, "moneyFlow": 120000000, "volRatio": 2.1, "turn": 5.2},
        {"code": "000858.SZ", "name": "五粮液", "price": 148.8, "rise": 1.8, "moneyFlow": 85000000, "volRatio": 1.9, "turn": 4.8},
    ]


def get_equity_curve():
    now = datetime.now()
    return [
        {"date": (now - timedelta(days=6)).strftime("%m/%d"), "total": 122000},
        {"date": (now - timedelta(days=5)).strftime("%m/%d"), "total": 123500},
        {"date": (now - timedelta(days=4)).strftime("%m/%d"), "total": 125200},
        {"date": (now - timedelta(days=3)).strftime("%m/%d"), "total": 124800},
        {"date": (now - timedelta(days=2)).strftime("%m/%d"), "total": 126100},
        {"date": (now - timedelta(days=1)).strftime("%m/%d"), "total": 127300},
        {"date": now.strftime("%m/%d"), "total": 128560},
    ]
