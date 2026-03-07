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
    """与 QMT.py 大盘环境一致，signal 可为 RED|YELLOW|STRONG_YELLOW|GREEN|STRONG_GREEN|SUPER_GREEN"""
    return {
        "signal": "GREEN",  # RED | YELLOW | STRONG_YELLOW | GREEN | STRONG_GREEN | SUPER_GREEN
        "shIndex": 3245.67,
        "shMa20": 3210.22,
        "shTodayReturn": 0.85,
        "dropDaysIn10": 1,
    }


def get_strategy_params():
    """与 QMT.py 策略参数完全一致（仓位梯度、买卖时间、止盈止损、选股条件）"""
    return {
        "maxPositionGreen": 0.70,   # QMT.py MAX_POSITION_GREEN
        "maxPositionYellow": 0.50,   # QMT.py MAX_POSITION_YELLOW
        "maxStocks": 3,             # QMT.py MAX_STOCKS_GREEN
        "minBuyVolume": 100,        # QMT.py MIN_BUY_VOLUME
        "maxDailyLossRatio": 0.015, # QMT.py MAX_DAILY_LOSS_RATIO 1.5%
        "buyTime": "14:50",         # QMT.py BUY_HOUR, BUY_MINUTE
        "sellStart": "09:30",       # QMT.py SELL_START_HOUR, SELL_START_MIN
        "sellEnd": "10:30",         # QMT.py SELL_END_HOUR, SELL_END_MIN
        "takeProfit": 3.0,          # QMT.py TAKE_PROFIT_1 阶梯止盈首档
        "stopLoss": -1.5,           # QMT.py STOP_LOSS
        "minPrice": 8,              # QMT.py MIN_PRICE
        "maxPrice": 40,             # QMT.py MAX_PRICE
        "minRise": 2.0,             # QMT.py MIN_RISE
        "maxRise": 4.0,             # QMT.py MAX_RISE
        # 仓位梯度（与 QMT.py 完全一致，供大屏展示）
        "positionTiers": [
            {"signal": "SUPER_GREEN", "label": "超强绿灯", "position": 0.85, "maxStocks": 4},
            {"signal": "STRONG_GREEN", "label": "强绿灯", "position": 0.75, "maxStocks": 4},
            {"signal": "GREEN", "label": "普通绿灯", "position": 0.70, "maxStocks": 3},
            {"signal": "STRONG_YELLOW", "label": "强黄灯", "position": 0.60, "maxStocks": 3},
            {"signal": "YELLOW", "label": "普通黄灯", "position": 0.50, "maxStocks": 2},
            {"signal": "RED", "label": "红灯", "position": 0.00, "maxStocks": 0},
        ],
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
