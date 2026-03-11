#coding:gbk
# -*- coding: utf-8 -*-
"""适配国金QMT极速策略交易系统 Python API（Python3）"""
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ===================== 核心配置（仅需修改这里） =====================
# 初始本金（用于风控计算，实际以账户为准）
INIT_CAPITAL = 100000.0
# 国金QMT 资金账号（在 init 中 set_account 用，请改为您的实际账号）
ACCOUNT_ID = '8885733900' # 资金账号
# ==================================================================

# ===================== 策略核心参数（完全保留原逻辑） =====================
# 仓位配置（梯度仓位，略加以提高资金利用率）
MAX_POSITION_SUPER_GREEN = 0.85   # 超强绿灯 → 85%
MAX_POSITION_STRONG_GREEN = 0.75  # 强绿灯 → 75%
MAX_POSITION_GREEN = 0.70         # 普通绿灯 → 70%
MAX_POSITION_STRONG_YELLOW = 0.60 # 强黄灯 → 60%
MAX_POSITION_YELLOW = 0.50        # 普通黄灯 → 50%
MAX_POSITION_RED = 0.00           # 红灯 → 0%

# 持仓数量限制
MAX_STOCKS_SUPER_GREEN = 4        # 超强绿灯最多4只
MAX_STOCKS_STRONG_GREEN = 4       # 强绿灯最多4只
MAX_STOCKS_GREEN = 3              # 普通绿灯最多3只
MAX_STOCKS_STRONG_YELLOW = 3      # 强黄灯最多3只
MAX_STOCKS_YELLOW = 2             # 普通黄灯最多2只

# 交易基础参数
MIN_BUY_VOLUME = 100              # 最小买100股
MAX_DAILY_LOSS_RATIO = 0.015      # 单日亏1.5%停止买入
MAX_DAILY_LOSS_CLEAR = 0.02       # 单日亏2%强制清仓

# 选股条件（最终版）
MIN_PRICE, MAX_PRICE = 8, 100      # 股价范围8-100元
MIN_RISE, MAX_RISE = 2.0, 5.0     # 涨幅范围2-5%
MIN_VOL_RATIO = 2.0                # 量比≥2
MIN_TURN, MAX_TURN = 4, 15         # 换手率范围 4%～15%（与 data['turn'] 一致，为 % 前的数字，非小数）
MIN_CAP = 5000000000             # 50亿市值
MAX_CAP = 30000000000            # 300亿市值
# 卖出规则（阶梯止盈）
TAKE_PROFIT_1 = 3.0    # 涨幅≥3%卖30%
TAKE_PROFIT_2 = 4.0    # 涨幅≥4%再卖30%（累计60%）
TAKE_PROFIT_3 = 5.0    # 涨幅≥5%再卖30%（累计90%）
TAKE_PROFIT_4 = 6.0    # 涨幅≥6%清仓剩余
STOP_LOSS = -1.5       # 亏损≤-1.5%止损
STOP_LOSS_EARLY = -1.0 # 亏损≤-1%且量比<1提前止损
SELL_CUTOFF_TIME = 10*60 + 15     # 10:15前未冲高卖出

# T+0参数
T0_BUY_DOWN = -0.5     # 回调至成本价-0.5%买回
T0_SELL_UP = 1.0       # 反弹≥1%卖出T0仓位
T0_MAX_RATIO = 1/3     # T0仓位不超过原持仓1/3

# 交易时间
BUY_HOUR, BUY_MINUTE = 14, 50    # 14:55-14:57买入
SELL_START_HOUR, SELL_START_MIN = 9, 30  # 9:30开始卖出
SELL_END_HOUR, SELL_END_MIN = 10, 30     # 10:30前必须卖完

# 监控大屏状态文件路径（QMT 策略运行时写入，后端 FastAPI 读取）
# QMT 下无 __file__ 且子进程可能拿不到 bat 的环境变量，这里直接写死你项目的路径，保证能写出文件
import os as _os
try:
    _script_dir = _os.path.dirname(_os.path.abspath(__file__))
    _default_path = _os.path.join(_script_dir, "strategy_state.json")
except NameError:
    # QMT 里跑时用这个路径，请按你本机项目位置改成绝对路径
    _default_path = r"d:\Automated-stocks\backend\strategy_state.json"
DASHBOARD_STATE_PATH = _os.environ.get("DASHBOARD_STATE_PATH", _default_path)

# ===================== QMT API 适配层 =====================

def _qmt_get_market_data(ContextInfo, fields, stock_code, period='1d', count=-1):
    """
    兼容 QMT 多种返回格式：DataFrame/Series（按日期或代码为索引）或 dict{code: data}。
    统一输出：{code: {field: [value, ...]}}
    """
    if not isinstance(stock_code, list):
        stock_code = [stock_code]
    if not isinstance(fields, list):
        fields = [fields]
    req_count = count if count > 0 else 1

    try:
        raw_data = ContextInfo.get_market_data_ex(
            fields=fields,
            stock_code=stock_code,
            period=period,
            start_time='',
            end_time='',
            count=req_count,
            dividend_type='front',
            fill_data=True,
            subscribe=True
        )
        # 空数据校验
        if raw_data is None:
            print(f"⚠️ get_market_data_ex 返回 None，股票={stock_code}，字段={fields}")
            return {}
        if isinstance(raw_data, pd.DataFrame) and raw_data.empty:
            print(f"⚠️ get_market_data_ex 返回空 DataFrame，股票={stock_code}，字段={fields}")
            return {}

        result = {}

        # ---------- 1. 返回的是 DataFrame（QMT 常见：单股多日 index=日期，多股 index=代码）----------
        if isinstance(raw_data, pd.DataFrame):
            df = raw_data
            # 单股
            if len(stock_code) == 1:
                code = stock_code[0]
                result[code] = {}
                # 情况A：columns=字段（index=日期），最常见
                if any(f in df.columns for f in fields):
                    for f in fields:
                        if f in df.columns:
                            s = pd.to_numeric(df[f], errors='coerce').fillna(0.0)
                            result[code][f] = s.astype(float).tolist()
                        else:
                            result[code][f] = [0.0] * len(df)
                # 情况B：columns=股票代码（index=日期），该列为多日序列
                elif code in df.columns:
                    s = pd.to_numeric(df[code], errors='coerce').fillna(0.0)
                    vals = s.astype(float).tolist()
                    for f in fields:
                        result[code][f] = vals
                else:
                    for f in fields:
                        result[code][f] = [0.0] * len(df)
            else:
                # 多股：index 为股票代码
                for code in df.index:
                    c = str(code).strip()
                    result[c] = {}
                    for f in fields:
                        if f in df.columns and c in df.index:
                            try:
                                val = df.loc[code, f]
                                result[c][f] = [float(val)] if pd.api.types.is_scalar(val) else pd.to_numeric(val, errors='coerce').fillna(0.0).astype(float).tolist()
                            except Exception:
                                result[c][f] = [0.0]
                        else:
                            result[c][f] = [0.0]
            return result

        # ---------- 2. 返回的是 Series（单股单点或多字段单点）----------
        if isinstance(raw_data, pd.Series):
            if len(stock_code) == 1:
                code = stock_code[0]
                result[code] = {}
                for f in fields:
                    if f in raw_data.index:
                        try:
                            result[code][f] = [float(raw_data[f])]
                        except (ValueError, TypeError):
                            result[code][f] = [0.0]
                    else:
                        result[code][f] = [0.0]
                return result
            return {}

        # ---------- 3. 返回 dict：{code: data}，data 可能是 dict/list/DataFrame ----------
        if isinstance(raw_data, dict):
            for code in raw_data:
                result[code] = {}
                code_data = raw_data[code]

                if isinstance(code_data, dict):
                    for field in fields:
                        val = code_data.get(field, 0.0)
                        try:
                            float_val = float(val) if val is not None else 0.0
                        except (ValueError, TypeError):
                            float_val = 0.0
                        result[code][field] = [float_val]

                elif isinstance(code_data, list) and len(code_data) > 0:
                    for field in fields:
                        field_values = []
                        for time_point in code_data:
                            if isinstance(time_point, dict):
                                val = time_point.get(field, 0.0)
                                try:
                                    float_val = float(val) if val is not None else 0.0
                                except (ValueError, TypeError):
                                    float_val = 0.0
                                field_values.append(float_val)
                        result[code][field] = field_values

                elif isinstance(code_data, pd.DataFrame) and not code_data.empty:
                    for field in fields:
                        if field in code_data.columns:
                            s = pd.to_numeric(code_data[field], errors='coerce').fillna(0.0)
                            result[code][field] = s.astype(float).tolist()
                        else:
                            result[code][field] = [0.0] * len(code_data)

                else:
                    for field in fields:
                        result[code][field] = [0.0]

            return result

        # 未知类型时打印便于排查
        print(f"⚠️ get_market_data_ex 未知返回类型：{type(raw_data)}，股票={stock_code}")
        return {}

    except Exception as e:
        err_msg = f"❌ _qmt_get_market_data 异常：{str(e)}"
        print(err_msg)
        import traceback
        print(traceback.format_exc())
        return {}

def _qmt_log(ContextInfo, msg):
    """QMT 无 log 时用 print"""
    try:
        ContextInfo.log(msg)
    except Exception:
        print(msg)

# 全局变量（策略编辑器用ContextInfo存储）
def init_global_vars(ContextInfo):
    """初始化全局变量"""
    ContextInfo.HOLD_CODES = {}  # 持仓股: {成本价, 持仓数量, T0_flag}
    ContextInfo.T0_POSITIONS = {} # T0仓位记录
    ContextInfo._buy_done_date = None   # 当日已执行买入的日期，避免重复
    ContextInfo._sell_done_date = None  # 当日已执行卖出的日期，避免重复

# ===================== 大盘环境判断（适配 QMT） =====================
def get_env(ContextInfo):
    """判断大盘环境，返回环境类型和对应仓位"""
    sh = "000001.SH"
    try:
        k_data = _qmt_get_market_data(ContextInfo, ['close'], [sh], period='1d', count=21)
        if not k_data or sh not in k_data or len(k_data[sh]['close']) < 21:
            return "YELLOW", MAX_POSITION_YELLOW
        close_list = k_data[sh]['close']
        close_list = close_list[-21:]  # 取 21 根，shift(1)+dropna 后剩 20 行，才能满足 len(k_df)>=20
        k_df = pd.DataFrame({'close': close_list})
        k_df['pre_close'] = k_df['close'].shift(1)
        k_df = k_df.dropna()
        if len(k_df) < 20:
            return "YELLOW", MAX_POSITION_YELLOW
        k_df['ma20'] = k_df['close'].rolling(20).mean()
        close = k_df['close'].iloc[-1]
        ma20 = k_df['ma20'].iloc[-1]
        pre = k_df['pre_close'].iloc[-1]
        today_r = (close / pre - 1) * 100
        recent_10 = k_df.iloc[-10:]
        recent_10 = recent_10.copy()
        recent_10['rise'] = (recent_10['close'] / recent_10['pre_close'] - 1) * 100
        drop10 = len(recent_10[recent_10['rise'] <= -1])
        if close < ma20 or today_r <= -1.5 or drop10 >= 3:
            _qmt_log(ContextInfo, "🔴 红灯 → 空仓不买")
            return "RED", MAX_POSITION_RED
        if close > ma20 and today_r >= 1.5 and drop10 <= 0:
            _qmt_log(ContextInfo, "🟢 超强绿灯 → 80%仓位")
            return "SUPER_GREEN", MAX_POSITION_SUPER_GREEN
        elif close > ma20 and today_r >= 1.0 and drop10 <= 0:
            _qmt_log(ContextInfo, "🟢 强绿灯 → 70%仓位")
            return "STRONG_GREEN", MAX_POSITION_STRONG_GREEN
        elif close > ma20 and today_r >= 0.5 and drop10 <= 1:
            _qmt_log(ContextInfo, "🟢 普通绿灯 → 60%仓位")
            return "GREEN", MAX_POSITION_GREEN
        elif close > ma20 and today_r >= 0 and drop10 <= 1:
            _qmt_log(ContextInfo, "🟡 强黄灯 → 55%仓位")
            return "STRONG_YELLOW", MAX_POSITION_STRONG_YELLOW
        else:
            _qmt_log(ContextInfo, "🟡 普通黄灯 → 40%仓位")
            return "YELLOW", MAX_POSITION_YELLOW
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 环境判断出错：%s，默认黄灯" % str(e))
        return "YELLOW", MAX_POSITION_YELLOW

# ===================== 账户数据获取（QMT：get_trade_detail_data） =====================
def get_account_info(ContextInfo):
    """获取账户总资产和当日盈亏（QMT 用 get_trade_detail_data(accountID,'stock','account')）"""
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    if not accid:
        return {'total_asset': INIT_CAPITAL, 'today_pnl': 0.0, 'cash': 0.0}
    try:
        acct_list = get_trade_detail_data(accid, 'stock', 'account')
        if not acct_list:
            return {'total_asset': INIT_CAPITAL, 'today_pnl': 0.0, 'cash': 0.0}
        obj = acct_list[0]
        total_asset = float(getattr(obj, 'm_dBalance', 0) or 0)
        cash = float(getattr(obj, 'm_dAvailable', 0) or 0)
        today_pnl = float(getattr(obj, 'm_dPositionProfit', 0) or 0)
        return {'total_asset': total_asset or INIT_CAPITAL, 'today_pnl': today_pnl, 'cash': cash}
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 获取账户信息失败：%s" % str(e))
        return {'total_asset': INIT_CAPITAL, 'today_pnl': 0.0, 'cash': 0.0}

def get_stock_position(ContextInfo, code):
    """获取个股持仓（QMT 用 get_trade_detail_data 的 position，按 m_strInstrumentID 匹配）"""
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    if not accid:
        return {'volume': 0, 'can_use': 0, 'cost': 0.0}
    try:
        pos_list = get_trade_detail_data(accid, 'stock', 'position')
        for obj in pos_list or []:
            sid = getattr(obj, 'm_strInstrumentID', '') or ''
            if sid == code or sid.replace('.', '') == code.replace('.', ''):
                return {
                    'volume': int(getattr(obj, 'm_nVolume', 0) or 0),
                    'can_use': int(getattr(obj, 'm_nCanUseVolume', 0) or 0),
                    'cost': float(getattr(obj, 'm_dOpenPrice', 0) or 0)
                }
        return {'volume': 0, 'can_use': 0, 'cost': 0.0}
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 获取%s持仓失败：%s" % (code, str(e)))
        return {'volume': 0, 'can_use': 0, 'cost': 0.0}

# ===================== 选股模块（适配 QMT 行情与合约接口） =====================
def get_board_rate(ContextInfo, code):
    """涨停开板率（QMT 用 get_full_tick + get_instrumentdetail 的 UpStopPrice）"""
    try:
        tick_data = ContextInfo.get_full_tick(stock_code=[code])
        if not tick_data or code not in tick_data:
            return 1.0
        tick = tick_data[code]
        last_price = float(tick.get('lastPrice', 0) or tick.get('lastClose', 0))
        detail = ContextInfo.get_instrumentdetail(code)
        if not detail or not isinstance(detail, dict):
            return 1.0
        limit_up = float(detail.get('UpStopPrice', 0) or 0)
        if limit_up <= 0:
            return 1.0
        if last_price < limit_up:
            return 0.0
        return 0.0 if last_price >= limit_up else 0.2
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 获取%s开板率失败：%s" % (code, str(e)))
        return 1.0

def get_stock_data(ContextInfo, code):
    """获取个股核心数据（QMT：get_market_data 字段可能无 vol_ratio/turnover/float_mktcap/net_main_inflow，用可获字段近似）"""
    try:
        fields_quote = ['close', 'open', 'high', 'low', 'volume', 'amount', 'turnover']
        quote = _qmt_get_market_data(ContextInfo, fields_quote, [code], period='1d', count=1)
        kline = _qmt_get_market_data(ContextInfo, ['close', 'volume'], [code], period='1d', count=20)
        if code not in quote or code not in kline or len(kline[code]['close']) < 20:
            return None
        q = quote[code]
        close = q['close'][0] if q['close'] else 0
        open_ = q['open'][0] if q.get('open') and q['open'] else close
        amount_ = q['amount'][0] if q.get('amount') and q['amount'] else 0
        pre_close = kline[code]['close'][-2] if len(kline[code]['close']) >= 2 else close
        vol_ratio = 1.0
        # 换手率：get_market_data_ex 的 K 线常无 turnover 字段，先尝试 API，否则用 成交量/流通股 计算
        vol = float(q['volume'][0]) if (q.get('volume') and q['volume']) else 0.0
        turnover_raw = 0.0
        if q.get('turnover') and q['turnover']:
            try:
                v = float(q['turnover'][0])
                # API 可能为小数（0.05=5%）或已是百分数（5 表示 5%）
                turnover_raw = v if v > 1 else v * 100.0
            except (TypeError, IndexError):
                pass
        turn_percent = turnover_raw if turnover_raw else 0.0
        float_mktcap = 0.0
        net_main_inflow = 0.0
        # 量比 = (当前总手 ÷ 已交易分钟数) ÷ 过去5日平均每分钟成交量
        # A 股 9:30-11:30(120min) + 13:00-15:00(120min) = 240min/日
        kline_vol = kline[code].get('volume') or []
        if vol and kline_vol and len(kline_vol) >= 6:
            past_vols = [float(x) for x in kline_vol[-6:-1] if x is not None]
            if len(past_vols) >= 1:
                now = datetime.now()
                if now.hour < 9 or (now.hour == 9 and now.minute < 30):
                    minutes_elapsed = 1  # 未开市避免除零
                elif now.hour < 11 or (now.hour == 11 and now.minute <= 30):
                    minutes_elapsed = (now.hour - 9) * 60 + (now.minute - 30)  # 9:30~11:30
                    minutes_elapsed = max(1, min(120, minutes_elapsed))
                elif now.hour < 13:
                    minutes_elapsed = 120  # 午休
                elif now.hour < 15 or (now.hour == 15 and now.minute == 0):
                    minutes_elapsed = 120 + (now.hour - 13) * 60 + now.minute  # 13:00~15:00
                    minutes_elapsed = max(121, min(240, minutes_elapsed))
                else:
                    minutes_elapsed = 240  # 收盘后
                sum_past_5 = sum(past_vols)
                if sum_past_5 > 0:
                    avg_per_min_past5 = sum_past_5 / (5 * 240.0)  # 过去5日平均每分钟成交量(手)
                    vol_per_min_today = vol / float(minutes_elapsed)  # 当前平均每分钟成交量(手)
                    vol_ratio = vol_per_min_today / avg_per_min_past5 if avg_per_min_past5 > 0 else 1.0
        detail = ContextInfo.get_instrumentdetail(code)
        if detail and isinstance(detail, dict):
            float_vol = detail.get('FloatVolumn') or detail.get('FloatVolume') or 0
            if float_vol and close:
                float_mktcap = float(float_vol) * float(close)
            # API 无换手率时用 成交量/流通股 计算（与实盘显示一致）
            # 注意：get_market_data_ex 的 volume 单位是「手」(1手=100股)，流通股单位是「股」，需先换算
            if turn_percent == 0 and float_vol and vol:
                try:
                    vol_in_shares = vol * 100.0  # 手 → 股
                    turn_percent = (vol_in_shares / float(float_vol)) * 100.0
                except (ZeroDivisionError, TypeError):
                    pass
        name = (detail.get('InstrumentName') or '') if detail and isinstance(detail, dict) else ''
        close_list = kline[code]['close']
        data = {
            'code': code,
            'price': close,
            'rise': (close / pre_close - 1) * 100 if pre_close else 0,
            'vol_ratio': vol_ratio,
            'turn': turn_percent,
            'cap': float_mktcap or MIN_CAP,
            'money': net_main_inflow or 0,
            'amount': amount_,
            'ma5': sum(close_list[-5:]) / 5,
            'ma10': sum(close_list[-10:]) / 10,
            'ma20': sum(close_list) / 20,
            'pre': pre_close,
            'board_rate': get_board_rate(ContextInfo, code),
            'name': name
        }
        return data
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 获取%s数据失败：%s" % (code, str(e)))
        return None

def select_stocks(ContextInfo, env_type):
    """选股：按综合评分排序（QMT：get_stock_list_in_sector）"""
    max_stocks = {
        'SUPER_GREEN': MAX_STOCKS_SUPER_GREEN,
        'STRONG_GREEN': MAX_STOCKS_STRONG_GREEN,
        'GREEN': MAX_STOCKS_GREEN,
        'STRONG_YELLOW': MAX_STOCKS_STRONG_YELLOW,
        'YELLOW': MAX_STOCKS_YELLOW,
        'RED': 0
    }.get(env_type, 0)
    if max_stocks == 0:
        return []
    try:
        all_stocks = ContextInfo.get_stock_list_in_sector('沪深A股', False)
    except Exception:
        all_stocks = ContextInfo.get_stock_list_in_sector('沪深A股')
    if not all_stocks:
        return []
    to_scan = list(all_stocks) if not isinstance(all_stocks, (list, tuple)) else all_stocks
    total = len(to_scan)
    _qmt_log(ContextInfo, "选股：共%d只待筛选" % total)
    _qmt_log(ContextInfo, "筛选阈值：价[%s,%s]元 涨[%s,%s]%% 量比≥%s 换手[%s,%s]%% 市值[%s,%s]亿 ma5>ma10>ma20" % (
        MIN_PRICE, MAX_PRICE, MIN_RISE, MAX_RISE, MIN_VOL_RATIO, MIN_TURN, MAX_TURN,
        MIN_CAP / 1e8, MAX_CAP / 1e8))
    valid_stocks = []
    no_data_count = 0
    fail_reasons = {'price': 0, 'rise': 0, 'vol_ratio': 0, 'turn': 0, 'cap': 0, 'ma': 0, 'st': 0}
    fail_examples = []
    for i, code in enumerate(to_scan):
        if (i + 1) % 500 == 0 or i == 0:
            _qmt_log(ContextInfo, "选股进度：%d/%d，已得有效 %d 只" % (i + 1, total, len(valid_stocks)))
        if not code or not isinstance(code, str):
            continue
        if not (code.startswith(('60', '00', '30')) or '.SH' in code or '.SZ' in code):
            if code.startswith(('6', '5')):
                code = code + '.SH' if '.' not in code else code
            elif code.startswith(('0', '3')):
                code = code + '.SZ' if '.' not in code else code
            else:
                continue
        if '.' not in code:
            code = code + '.SH' if code.startswith(('6', '5')) else code + '.SZ'
        data = get_stock_data(ContextInfo, code)
        if not data:
            no_data_count += 1
            continue
        reasons = []
        if not (MIN_PRICE <= data['price'] <= MAX_PRICE):
            reasons.append('price(%.2f)' % data['price'])
            fail_reasons['price'] += 1
        if not (MIN_RISE <= data['rise'] <= MAX_RISE):
            reasons.append('rise(%.2f%%)' % data['rise'])
            fail_reasons['rise'] += 1
        if data['vol_ratio'] < MIN_VOL_RATIO:
            reasons.append('vol_ratio(%.2f)' % data['vol_ratio'])
            fail_reasons['vol_ratio'] += 1
        if not (MIN_TURN <= data['turn'] <= MAX_TURN):
            reasons.append('turn(%.2f)' % data['turn'])
            fail_reasons['turn'] += 1
        if not (MIN_CAP <= data['cap'] <= MAX_CAP):
            reasons.append('cap(%.0f亿)' % (data['cap'] / 1e8))
            fail_reasons['cap'] += 1
        ma_ok = data['ma5'] > data['ma10'] > data['ma20']
        if not ma_ok:
            reasons.append('ma(5=%.2f 10=%.2f 20=%.2f)' % (data['ma5'], data['ma10'], data['ma20']))
            fail_reasons['ma'] += 1
        if 'ST' in (data.get('name') or ''):
            reasons.append('ST')
            fail_reasons['st'] += 1
        if not reasons:
            data['score'] = data['amount'] * data['vol_ratio'] * max(data['rise'], 0.01)
            valid_stocks.append(data)
        else:
            if len(fail_examples) < 5:
                fail_examples.append((code, data.get('name', ''), reasons, data))
    _qmt_log(ContextInfo, "-------- 筛选统计 --------")
    _qmt_log(ContextInfo, "无行情数据(跳过): %d 只" % no_data_count)
    _qmt_log(ContextInfo, "未通过条件统计(同一只可能触达多条件): price=%d rise=%d vol_ratio=%d turn=%d cap=%d ma=%d ST=%d" % (
        fail_reasons['price'], fail_reasons['rise'], fail_reasons['vol_ratio'], fail_reasons['turn'],
        fail_reasons['cap'], fail_reasons['ma'], fail_reasons['st']))
    for code, name, reasons, d in fail_examples:
        _qmt_log(ContextInfo, "  示例未通过: %s %s | 原因: %s | 价=%.2f 涨=%.2f%% 量比=%.2f 换手=%.2f 市值=%.0f亿 ma5=%.2f ma10=%.2f ma20=%.2f 成交额=%.0f" % (
            code, name, ','.join(reasons), d.get('price', 0), d.get('rise', 0), d.get('vol_ratio', 0), d.get('turn', 0),
            d.get('cap', 0) / 1e8, d.get('ma5', 0), d.get('ma10', 0), d.get('ma20', 0), d.get('amount', 0)))
    _qmt_log(ContextInfo, "有效股票（%d只）：%s" % (len(valid_stocks), [s['code'] for s in valid_stocks]))
    valid_stocks.sort(key=lambda x: x['score'], reverse=True)
    selected = valid_stocks[:max_stocks]
    _qmt_log(ContextInfo, "\n✅ 选股结果（共%d只）：" % len(selected))
    for stock in selected:
        _qmt_log(ContextInfo, "   %s %s - 评分：%.0f 涨幅：%.2f%%" % (stock['code'], stock['name'], stock['score'], stock['rise']))
    return selected

# ===================== 交易执行（QMT：passorder） =====================
# 格式：passorder(opType, orderType, accountid, orderCode, prType, modelprice, volume, '', 1, '', ContextInfo)
def buy_stock(ContextInfo, code, volume, price):
    """买入（单股单账号股票最新价）"""
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    if not accid:
        _qmt_log(ContextInfo, "❌ 未设置资金账号，无法买入")
        return False
    try:
        passorder(23, 1101, accid, code, 5, 0, int(volume), '', 1, '', ContextInfo)
        _qmt_log(ContextInfo, "✅ 委托买入 %s %d股，单价：%.2f元" % (code, int(volume), price))
        return True
    except Exception as e:
        _qmt_log(ContextInfo, "❌ 买入 %s 失败：%s" % (code, str(e)))
        return False

def sell_stock(ContextInfo, code, volume, price):
    """卖出（单股单账号股票最新价）"""
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    if not accid:
        _qmt_log(ContextInfo, "❌ 未设置资金账号，无法卖出")
        return False
    try:
        passorder(24, 1101, accid, code, 5, 0, int(volume), '', 1, '', ContextInfo)
        _qmt_log(ContextInfo, "✅ 委托卖出 %s %d股，单价：%.2f元" % (code, int(volume), price))
        return True
    except Exception as e:
        _qmt_log(ContextInfo, "❌ 卖出 %s 失败：%s" % (code, str(e)))
        return False

def buy_stocks(ContextInfo):
    """买入执行（梯度仓位+资金优化分配）"""
    env_type, position_ratio = get_env(ContextInfo)
    if env_type == "RED":
        print("红灯环境，不买入")
        return
    account = get_account_info(ContextInfo)
    total_asset = account['total_asset']
    today_pnl = account['today_pnl']
    if today_pnl <= -total_asset * MAX_DAILY_LOSS_CLEAR:
        _qmt_log(ContextInfo, "⚠️ 当日亏损超2%%，强制清仓！")
        sell_all_positions(ContextInfo)
        return
    if today_pnl <= -total_asset * MAX_DAILY_LOSS_RATIO:
        _qmt_log(ContextInfo, "⚠️ 当日亏损超1.5%%，停止买入")
        return
    selected_stocks = select_stocks(ContextInfo, env_type)
    print("选股结果：" + str(selected_stocks))
    if not selected_stocks:
        _qmt_log(ContextInfo, "❌ 无符合条件股票")
        return
    buy_capital = total_asset * position_ratio
    stock_count = len(selected_stocks)
    if stock_count == 0:
        print("无符合条件股票，不买入")
        return
    _qmt_log(ContextInfo, "\n💰 账户总资产：%.0f元，可买金额：%.0f元" % (total_asset, buy_capital))
    buy_amounts = []
    first_amount = buy_capital * 0.6   # 首笔集中：60%给评分第一的标的
    rest_amount = (buy_capital - first_amount) / (stock_count - 1) if stock_count > 1 else 0
    for i in range(stock_count):
        buy_amounts.append(first_amount if i == 0 else rest_amount)
    ContextInfo.HOLD_CODES = {}
    for i, stock in enumerate(selected_stocks):
        code = stock['code']
        price = stock['price']
        amount = buy_amounts[i]
        volume = int(amount / price) // 100 * 100
        volume = max(volume, MIN_BUY_VOLUME)
        if stock['turn'] >= 10:
            volume = max(volume // 2, MIN_BUY_VOLUME)
            _qmt_log(ContextInfo, "⚠️ %s 换手率≥10%%，买入数量减半：%d股" % (code, volume))
        if volume < MIN_BUY_VOLUME:
            continue
        if buy_stock(ContextInfo, code, volume, price):
            ContextInfo.HOLD_CODES[code] = {'cost': price, 'volume': volume, 't0_flag': False}

def sell_stocks(ContextInfo):
    """卖出执行（阶梯止盈+止损）"""
    if not getattr(ContextInfo, 'HOLD_CODES', None) and not getattr(ContextInfo, 'T0_POSITIONS', None):
        return
    _qmt_log(ContextInfo, "\n📤 执行卖出操作：")
    current_time = datetime.now()
    current_minute = current_time.hour * 60 + current_time.minute
    for code in list(getattr(ContextInfo, 'HOLD_CODES', {}).keys()):
        pos = get_stock_position(ContextInfo, code)
        if pos['can_use'] == 0:
            continue
        data = get_stock_data(ContextInfo, code)
        if not data:
            sell_stock(ContextInfo, code, pos['can_use'], 0.0)
            _qmt_log(ContextInfo, "❌ %s 数据异常，兜底卖出 %d股" % (code, pos['can_use']))
            if hasattr(ContextInfo, 'HOLD_CODES') and code in ContextInfo.HOLD_CODES:
                del ContextInfo.HOLD_CODES[code]
            continue
        current_price = data['price']
        current_rise = (current_price / data['pre'] - 1) * 100 if data['pre'] else 0
        hold_volume = pos['can_use']
        if current_rise <= STOP_LOSS_EARLY and data['vol_ratio'] < 1.0:
            sell_stock(ContextInfo, code, hold_volume, current_price)
            _qmt_log(ContextInfo, "🔴 %s 提前止损：跌幅%.2f%%，卖出%d股" % (code, current_rise, hold_volume))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                del ContextInfo.HOLD_CODES[code]
            continue
        if current_rise <= STOP_LOSS:
            sell_stock(ContextInfo, code, hold_volume, current_price)
            _qmt_log(ContextInfo, "🔴 %s 止损：跌幅%.2f%%，卖出%d股" % (code, current_rise, hold_volume))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                del ContextInfo.HOLD_CODES[code]
            continue
        if current_rise >= TAKE_PROFIT_4:
            sell_stock(ContextInfo, code, hold_volume, current_price)
            _qmt_log(ContextInfo, "🟢 %s 止盈6%%：涨幅%.2f%%，卖出%d股" % (code, current_rise, hold_volume))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                del ContextInfo.HOLD_CODES[code]
        elif current_rise >= TAKE_PROFIT_3:
            sell_vol = int(hold_volume * 0.9)
            sell_stock(ContextInfo, code, sell_vol, current_price)
            _qmt_log(ContextInfo, "🟢 %s 止盈5%%：涨幅%.2f%%，卖出%d股" % (code, current_rise, sell_vol))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                ContextInfo.HOLD_CODES[code]['volume'] = hold_volume - sell_vol
        elif current_rise >= TAKE_PROFIT_2:
            sell_vol = int(hold_volume * 0.6)
            sell_stock(ContextInfo, code, sell_vol, current_price)
            _qmt_log(ContextInfo, "🟢 %s 止盈4%%：涨幅%.2f%%，卖出%d股" % (code, current_rise, sell_vol))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                ContextInfo.HOLD_CODES[code]['volume'] = hold_volume - sell_vol
        elif current_rise >= TAKE_PROFIT_1:
            sell_vol = int(hold_volume * 0.3)
            sell_stock(ContextInfo, code, sell_vol, current_price)
            _qmt_log(ContextInfo, "🟢 %s 止盈3%%：涨幅%.2f%%，卖出%d股" % (code, current_rise, sell_vol))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                ContextInfo.HOLD_CODES[code]['volume'] = hold_volume - sell_vol
        elif current_minute >= SELL_CUTOFF_TIME:
            sell_stock(ContextInfo, code, hold_volume, current_price)
            _qmt_log(ContextInfo, "⏰ %s 10:15未冲高，卖出%d股" % (code, hold_volume))
            if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                del ContextInfo.HOLD_CODES[code]
    handle_t0(ContextInfo)
    if current_minute >= SELL_END_HOUR * 60 + SELL_END_MIN:
        for code in list(getattr(ContextInfo, 'HOLD_CODES', {}).keys()):
            pos = get_stock_position(ContextInfo, code)
            if pos['can_use'] > 0:
                sell_stock(ContextInfo, code, pos['can_use'], 0.0)
                _qmt_log(ContextInfo, "⏰ %s 10:30强制清仓，卖出%d股" % (code, pos['can_use']))
                if code in getattr(ContextInfo, 'HOLD_CODES', {}):
                    del ContextInfo.HOLD_CODES[code]

def handle_t0(ContextInfo):
    """处理日内T+0"""
    for code in list(getattr(ContextInfo, 'T0_POSITIONS', {}).keys()):
        pos = get_stock_position(ContextInfo, code)
        if pos['can_use'] == 0:
            if code in getattr(ContextInfo, 'T0_POSITIONS', {}):
                del ContextInfo.T0_POSITIONS[code]
            continue
        data = get_stock_data(ContextInfo, code)
        if not data:
            continue
        current_price = data['price']
        t0_cost = ContextInfo.T0_POSITIONS[code]['cost']
        rise = (current_price / t0_cost - 1) * 100
        if rise >= T0_SELL_UP:
            sell_stock(ContextInfo, code, pos['can_use'], current_price)
            _qmt_log(ContextInfo, "📈 T+0止盈 %s：盈利%.2f%%，卖出%d股" % (code, rise, pos['can_use']))
            if code in getattr(ContextInfo, 'T0_POSITIONS', {}):
                del ContextInfo.T0_POSITIONS[code]
    for code in list(getattr(ContextInfo, 'HOLD_CODES', {}).keys()):
        if code in getattr(ContextInfo, 'T0_POSITIONS', {}):
            continue
        pos = get_stock_position(ContextInfo, code)
        if pos['can_use'] == 0:
            continue
        data = get_stock_data(ContextInfo, code)
        if not data:
            continue
        current_price = data['price']
        cost_price = ContextInfo.HOLD_CODES[code]['cost']
        drop = (current_price / cost_price - 1) * 100
        if drop <= T0_BUY_DOWN and data['vol_ratio'] >= 1.2:
            t0_volume = int(pos['volume'] * T0_MAX_RATIO) // 100 * 100
            t0_volume = max(t0_volume, MIN_BUY_VOLUME)
            if t0_volume > 0:
                buy_stock(ContextInfo, code, t0_volume, current_price)
                _qmt_log(ContextInfo, "📉 T+0买入 %s：回调%.2f%%，买入%d股" % (code, drop, t0_volume))
                ContextInfo.T0_POSITIONS[code] = {'cost': current_price, 'volume': t0_volume}
                ContextInfo.HOLD_CODES[code]['t0_flag'] = True

def sell_all_positions(ContextInfo):
    """强制清仓（QMT：get_trade_detail_data position 逐只卖出）"""
    _qmt_log(ContextInfo, "⚠️ 执行强制清仓")
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    if not accid:
        ContextInfo.HOLD_CODES = {}
        ContextInfo.T0_POSITIONS = {}
        return
    try:
        pos_list = get_trade_detail_data(accid, 'stock', 'position')
        for obj in pos_list or []:
            code = getattr(obj, 'm_strInstrumentID', '')
            can_use = int(getattr(obj, 'm_nCanUseVolume', 0) or 0)
            if code and can_use > 0:
                sell_stock(ContextInfo, code, can_use, 0.0)
    except Exception as e:
        _qmt_log(ContextInfo, "清仓异常：%s" % str(e))
    ContextInfo.HOLD_CODES = {}
    ContextInfo.T0_POSITIONS = {}

# ===================== 监控大屏状态导出（供本项目后端读取） =====================
def _get_market_env_detail(ContextInfo):
    """获取大盘环境详情，与 get_env 逻辑一致，返回前端所需字段"""
    sh = "000001.SH"
    try:
        k_data = _qmt_get_market_data(ContextInfo, ['close'], [sh], period='1d', count=21)
        if not k_data or sh not in k_data or len(k_data[sh]['close']) < 21:
            return {"signal": "YELLOW", "shIndex": 0, "shMa20": 0, "shTodayReturn": 0, "dropDaysIn10": 0}
        close_list = k_data[sh]['close'][-21:]
        k_df = pd.DataFrame({'close': close_list})
        k_df['pre_close'] = k_df['close'].shift(1)
        k_df = k_df.dropna()
        if len(k_df) < 20:
            return {"signal": "YELLOW", "shIndex": 0, "shMa20": 0, "shTodayReturn": 0, "dropDaysIn10": 0}
        k_df['ma20'] = k_df['close'].rolling(20).mean()
        close = float(k_df['close'].iloc[-1])
        ma20 = float(k_df['ma20'].iloc[-1])
        pre = float(k_df['pre_close'].iloc[-1])
        today_r = (close / pre - 1) * 100
        recent_10 = k_df.iloc[-10:].copy()
        recent_10['rise'] = (recent_10['close'] / recent_10['pre_close'] - 1) * 100
        drop10 = int(len(recent_10[recent_10['rise'] <= -1]))
        signal, _ = get_env(ContextInfo)
        return {"signal": signal, "shIndex": round(close, 2), "shMa20": round(ma20, 2),
                "shTodayReturn": round(today_r, 2), "dropDaysIn10": drop10}
    except Exception:
        return {"signal": "YELLOW", "shIndex": 0, "shMa20": 0, "shTodayReturn": 0, "dropDaysIn10": 0}


def _build_dashboard_state(ContextInfo):
    """组装与前端/后端 mock_data 一致的状态结构"""
    now = datetime.now()
    acc = get_account_info(ContextInfo)
    total_asset = acc.get('total_asset') or INIT_CAPITAL
    cash = acc.get('cash') or 0.0
    today_pnl = acc.get('today_pnl') or 0.0
    today_pnl_ratio = (today_pnl / total_asset * 100) if total_asset else 0.0
    env_detail = _get_market_env_detail(ContextInfo)
    hold_codes = getattr(ContextInfo, 'HOLD_CODES', {}) or {}
    holdings = []
    for code, info in hold_codes.items():
        cost = info.get('cost') or 0
        vol = info.get('volume') or 0
        if not vol:
            continue
        sd = get_stock_data(ContextInfo, code)
        if sd:
            price = sd.get('price') or cost
            name = sd.get('name') or code
        else:
            price = cost
            name = code
        pnl_ratio = ((price - cost) / cost * 100) if cost else 0
        holdings.append({
            "code": code, "name": name, "volume": vol, "costPrice": cost,
            "currentPrice": round(price, 2), "pnlRatio": round(pnl_ratio, 2)
        })
    accid = getattr(ContextInfo, 'accid', None) or ACCOUNT_ID
    account_id_display = ("****" + str(accid)[-4:]) if accid and len(str(accid)) >= 4 else "****"
    state = {
        "updated_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "connection": {
            "connected": True,
            "lastHeartbeat": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "accountId": account_id_display,
            "qmtHost": "QMT",
        },
        "account": {
            "totalAsset": round(total_asset, 2),
            "available": round(cash, 2),
            "todayPnl": round(today_pnl, 2),
            "todayPnlRatio": round(today_pnl_ratio, 2),
            "dailyLossLimitHit": total_asset > 0 and (today_pnl / total_asset <= -0.02),
        },
        "market_env": env_detail,
        "strategy_params": {
            "maxPositionGreen": MAX_POSITION_GREEN,
            "maxPositionYellow": MAX_POSITION_YELLOW,
            "maxStocks": MAX_STOCKS_GREEN,
            "minBuyVolume": MIN_BUY_VOLUME,
            "maxDailyLossRatio": MAX_DAILY_LOSS_RATIO,
            "buyTime": "%02d:%02d" % (BUY_HOUR, BUY_MINUTE),
            "sellStart": "%02d:%02d" % (SELL_START_HOUR, SELL_START_MIN),
            "sellEnd": "%02d:%02d" % (SELL_END_HOUR, SELL_END_MIN),
            "takeProfit": TAKE_PROFIT_1,
            "stopLoss": STOP_LOSS,
            "minPrice": MIN_PRICE,
            "maxPrice": MAX_PRICE,
            "minRise": MIN_RISE,
            "maxRise": MAX_RISE,
            "positionTiers": [
                {"signal": "SUPER_GREEN", "label": "超强绿灯", "position": MAX_POSITION_SUPER_GREEN, "maxStocks": MAX_STOCKS_SUPER_GREEN},
                {"signal": "STRONG_GREEN", "label": "强绿灯", "position": MAX_POSITION_STRONG_GREEN, "maxStocks": MAX_STOCKS_STRONG_GREEN},
                {"signal": "GREEN", "label": "普通绿灯", "position": MAX_POSITION_GREEN, "maxStocks": MAX_STOCKS_GREEN},
                {"signal": "STRONG_YELLOW", "label": "强黄灯", "position": MAX_POSITION_STRONG_YELLOW, "maxStocks": MAX_STOCKS_STRONG_YELLOW},
                {"signal": "YELLOW", "label": "普通黄灯", "position": MAX_POSITION_YELLOW, "maxStocks": MAX_STOCKS_YELLOW},
                {"signal": "RED", "label": "红灯", "position": MAX_POSITION_RED, "maxStocks": 0},
            ],
        },
        "holdings": holdings,
        "trades": [],
        "schedule": {
            "now": now.strftime("%Y-%m-%d %H:%M:%S"),
            "nextBuy": "今日 %02d:%02d" % (BUY_HOUR, BUY_MINUTE),
            "nextSell": "明日 %02d:%02d - %02d:%02d" % (SELL_START_HOUR, SELL_START_MIN, SELL_END_HOUR, SELL_END_MIN),
            "isWeekend": now.weekday() >= 5,
        },
        "candidates": [],
        "equity": [],
    }
    return state


def write_state_to_dashboard(ContextInfo):
    """将当前策略状态写入状态文件，供本项目后端 API 读取并展示到监控大屏"""
    if not DASHBOARD_STATE_PATH or not DASHBOARD_STATE_PATH.strip():
        return
    try:
        import json
        state = _build_dashboard_state(ContextInfo)
        with open(DASHBOARD_STATE_PATH.strip(), 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _qmt_log(ContextInfo, "⚠️ 写入监控状态文件失败: %s" % str(e))

# ===================== QMT 策略入口（必须实现） =====================
def init(ContextInfo):
    """策略初始化（QMT 要求：init 与 handlebar 必实现；set_account 绑定资金账号）"""
    init_global_vars(ContextInfo)
    accid = ACCOUNT_ID.strip() or getattr(ContextInfo, 'accid', '')
    if accid:
        ContextInfo.set_account(accid)
        ContextInfo.accid = accid
    _qmt_log(ContextInfo, "✅ 策略初始化完成，等待交易时间触发")

def handlebar(ContextInfo):
    if not ContextInfo.is_last_bar():
        return
    """策略主循环（QMT：每根 K 线调用一次；1 分钟周期时 14:50–14:52 会多次进入，用 _buy_done_date 当日只买一次）"""
    now = datetime.now()
    if now.weekday() >= 5:
        return
    today = now.date()
    current_hour = now.hour
    current_minute = now.minute
    current_second = now.second
    if current_hour == BUY_HOUR and BUY_MINUTE <= current_minute <= BUY_MINUTE + 2:
        if 0 <= current_second <= 15:
            if getattr(ContextInfo, '_buy_done_date', None) != today:
                ContextInfo._buy_done_date = today
                buy_stocks(ContextInfo)
    elif SELL_START_HOUR <= current_hour <= SELL_END_HOUR:
        if (current_hour == SELL_START_HOUR and SELL_START_MIN <= current_minute) or \
           (current_hour == SELL_END_HOUR and current_minute <= SELL_END_MIN):
            if getattr(ContextInfo, '_sell_done_date', None) != today:
                ContextInfo._sell_done_date = today
                sell_stocks(ContextInfo)
    write_state_to_dashboard(ContextInfo)
