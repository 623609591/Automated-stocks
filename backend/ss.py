# -*- coding: utf-8 -*-
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount
import time
from datetime import datetime

# ===================== 你只需要改这里 =====================
# 把这里换成你的【国金资金账号】（纯数字）
ACCOUNT_ID = "你的国金资金账号"
# ======================================================

# 仓位配置
MAX_POSITION_GREEN = 0.60   # 绿灯环境 → 用总资产60%
MAX_POSITION_YELLOW = 0.40  # 黄灯环境 → 用总资产40%
MAX_STOCKS = 3              # 最多只买3只
MIN_BUY_VOLUME = 100        # 最小买100股
MAX_DAILY_LOSS_RATIO = 0.02 # 单日亏2%自动停手

# 买卖时间
BUY_HOUR, BUY_MINUTE = 14, 50   # 14:50 买入
SELL_HOUR, SELL_START = 9, 30  # 09:30 开始卖出

# 选股条件（非常严格，只做强势安全股）
MIN_PRICE, MAX_PRICE = 8, 40
MIN_RISE, MAX_RISE = 1.5, 4.5
MIN_VOL_RATIO = 1.8
MIN_TURN, MAX_TURN = 4, 12
MIN_MONEY_FLOW = 30000000
MIN_CAP = 50000000000
MAX_CAP = 150000000000

# 卖出规则
TAKE_PROFIT = 3.0   # 盈利≥3% 自动止盈
STOP_LOSS  = -1.5   # 亏损≤-1.5% 自动止损
HOLD_CODES = []

# ===================== 大盘环境判断（绿灯/黄灯/红灯） =====================
def get_env():
    sh = "000001.SH"
    try:
        k = xtdata.get_local_kline(sh, '1d', 20)
        if len(k) < 20:
            return "YELLOW"
        
        close = k['close'].iloc[-1]
        ma20 = k['close'].rolling(20).mean().iloc[-1]
        pre = k['pre_close'].iloc[-1]
        today_r = (close / pre - 1) * 100
        drop10 = sum((k['close'].iloc[-10:] / k['pre_close'].iloc[-1:] - 1) * 100 <= -1)

        if close < ma20 or today_r <= -2 or drop10 >= 3:
            print("🔴 红灯 → 空仓不买")
            return "RED"
        if close > ma20 and today_r >= 0.5 and drop10 <= 1:
            print("🟢 绿灯 → 60%仓位")
            return "GREEN"
        print("🟡 黄灯 → 40%仓位")
        return "YELLOW"
    except:
        return "YELLOW"

# ===================== 获取总资产 =====================
def total_capital(trader, acc):
    try:
        return trader.get_account_total_asset(acc)['total_asset']
    except:
        return 50000.0

# ===================== 选股 =====================
def get_stock_data(code):
    try:
        quote = xtdata.get_market_data_ex([code], '1d', 1)[code]
        kline = xtdata.get_local_kline(code, '1d', 20)
        if not quote or not kline: return None
        
        price = quote['close'].iloc[-1]
        return {
            'price': price,
            'rise': (price / quote['pre_close'].iloc[-1] - 1) * 100,
            'vol_ratio': quote['vol_ratio'].iloc[-1],
            'turn': quote['turnover'].iloc[-1] * 100,
            'cap': quote['float_mktcap'].iloc[-1],
            'money': quote['net_main_inflow'].iloc[-1],
            'ma5': kline['close'].iloc[-5:].mean(),
            'ma10': kline['close'].iloc[-10:].mean(),
            'pre': quote['pre_close'].iloc[-1]
        }
    except:
        return None

# ===================== 自动买入 =====================
def buy_stocks(trader, acc):
    global HOLD_CODES
    env = get_env()
    if env == "RED":
        return

    cap = total_capital(trader, acc)
    max_total = cap * (MAX_POSITION_GREEN if env == "GREEN" else MAX_POSITION_YELLOW)
    print(f"总资产：{cap:.0f}元，可买：{max_total:.0f}元")

    # 单日大亏停止买入
    try:
        pnl = trader.get_account_pnl(acc)['today_pnl']
        if pnl <= -cap * MAX_DAILY_LOSS_RATIO:
            print("⚠️ 当日亏损超2%，停止买入")
            return
    except:
        pass

    # 全市场选股
    all_stocks = xtdata.get_stock_list_in_pool("沪深A股")
    valid = []
    for code in all_stocks:
        if not code.startswith(('60','00','30')): continue
        name = xtdata.get_instrument_detail(code).get('name','')
        if 'ST' in name: continue

        d = get_stock_data(code)
        if not d: continue

        if (MIN_PRICE <= d['price'] <= MAX_PRICE
            and MIN_RISE <= d['rise'] <= MAX_RISE
            and d['vol_ratio'] >= MIN_VOL_RATIO
            and MIN_TURN <= d['turn'] <= MAX_TURN
            and MIN_CAP <= d['cap'] <= MAX_CAP
            and d['money'] >= MIN_MONEY_FLOW
            and d['ma5'] > d['ma10']):
            valid.append((code, d['money'], d['price']))

    valid.sort(key=lambda x:x[1], reverse=True)
    valid = valid[:MAX_STOCKS]
    if not valid:
        print("❌ 无符合条件股票")
        return

    n = len(valid)
    per = max_total / n
    HOLD_CODES = []

    for code, _, price in valid:
        vol = int(per / price) // 100 * 100
        if vol < 100: vol = 100

        trader.order_stock(acc, code, 23, vol, 0, 0, "自动买入", "")
        print(f"✅ 买入 {code} {vol}股 单价{price:.2f}")
        HOLD_CODES.append(code)

    time.sleep(60)

# ===================== 自动卖出 =====================
def sell_stocks(trader, acc):
    global HOLD_CODES
    if not HOLD_CODES:
        return
    print("\n📤 执行早盘卖出")

    for code in HOLD_CODES.copy():
        d = get_stock_data(code)
        if not d:
            trader.order_stock(acc, code,24,100,0,0,"兜底卖出","")
            HOLD_CODES.remove(code)
            continue

        rise = (d['price'] / d['pre'] -1)*100
        pos = trader.query_stock_positions(acc, code)
        vol = pos['can_use_volume'] if pos else 0

        if vol <=0: vol = 100

        if rise >= TAKE_PROFIT:
            trader.order_stock(acc,code,24,vol,0,0,"止盈","")
            print(f"✅ {code} 止盈卖出 {vol}股")
        elif rise <= STOP_LOSS:
            trader.order_stock(acc,code,24,vol,0,0,"止损","")
            print(f"✅ {code} 止损卖出 {vol}股")
        else:
            trader.order_stock(acc,code,24,vol,0,0,"次日强制卖","")
            print(f"✅ {code} 强制卖出 {vol}股")
        HOLD_CODES.remove(code)
    time.sleep(30)

# ===================== 主程序 =====================
if __name__ == '__main__':
    acc = StockAccount(ACCOUNT_ID, "STOCK")
    trader = XtQuantTrader()
    trader.start()
    ret = trader.connect("127.0.0.1", 55666)

    if ret !=0:
        print("❌ 连接MiniQMT失败！请先登录MiniQMT！")
        exit()
    print("🚀 连接成功！尾盘自动策略已启动")

    while True:
        now = datetime.now()
        if now.weekday() >=5:
            time.sleep(60)
            continue

        # 14:50 买入
        if now.hour ==14 and now.minute ==50 and 0<=now.second<=15:
            buy_stocks(trader, acc)

        # 9:30~9:59 卖出
        if now.hour ==9 and 30<=now.minute<=59:
            sell_stocks(trader, acc)

        time.sleep(1)