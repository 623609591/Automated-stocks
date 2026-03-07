/**
 * 模拟数据 - 与 Python 策略逻辑对应
 * 实际对接时替换为调用后端 API（后端从 QMT 获取并暴露这些字段）
 */
import dayjs from 'dayjs'

export const getConnectionStatus = () => ({
  connected: true,
  lastHeartbeat: dayjs().toISOString(),
  accountId: '****1234',
  qmtHost: '127.0.0.1:55666',
})

export const getAccountOverview = () => ({
  totalAsset: 128560,
  available: 51200,
  todayPnl: 1260,
  todayPnlRatio: 0.99,
  dailyLossLimitHit: false, // 是否触发单日亏2%停手
})

export const getMarketEnv = () => ({
  signal: 'GREEN', // RED | YELLOW | STRONG_YELLOW | GREEN | STRONG_GREEN | SUPER_GREEN（与 QMT.py 一致）
  shIndex: 3245.67,
  shMa20: 3210.22,
  shTodayReturn: 0.85,
  dropDaysIn10: 1,
})

export const getStrategyParams = () => ({
  maxPositionGreen: 0.70,
  maxPositionYellow: 0.50,
  maxStocks: 3,
  minBuyVolume: 100,
  maxDailyLossRatio: 0.015,
  buyTime: '14:50',
  sellStart: '09:30',
  sellEnd: '10:30',
  takeProfit: 3.0,
  stopLoss: -1.5,
  minPrice: 8,
  maxPrice: 40,
  minRise: 2.0,
  maxRise: 4.0,
  positionTiers: [
    { signal: 'SUPER_GREEN', label: '超强绿灯', position: 0.85, maxStocks: 4 },
    { signal: 'STRONG_GREEN', label: '强绿灯', position: 0.75, maxStocks: 4 },
    { signal: 'GREEN', label: '普通绿灯', position: 0.70, maxStocks: 3 },
    { signal: 'STRONG_YELLOW', label: '强黄灯', position: 0.60, maxStocks: 3 },
    { signal: 'YELLOW', label: '普通黄灯', position: 0.50, maxStocks: 2 },
    { signal: 'RED', label: '红灯', position: 0.00, maxStocks: 0 },
  ],
})

export const getHoldings = () => [
  { code: '600519.SH', name: '贵州茅台', volume: 100, costPrice: 1680, currentPrice: 1720.5, pnlRatio: 2.41 },
  { code: '000858.SZ', name: '五粮液', volume: 200, costPrice: 145.2, currentPrice: 148.8, pnlRatio: 2.48 },
  { code: '300750.SZ', name: '宁德时代', volume: 100, costPrice: 198.5, currentPrice: 195.2, pnlRatio: -1.66 },
]

export const getTradeHistory = () => [
  { time: dayjs().subtract(1, 'hour').toISOString(), code: '600519.SH', name: '贵州茅台', side: 'buy', volume: 100, price: 1680, reason: '自动买入' },
  { time: dayjs().subtract(2, 'day').toISOString(), code: '000001.SZ', name: '平安银行', side: 'sell', volume: 200, price: 12.35, reason: '止盈' },
  { time: dayjs().subtract(3, 'day').toISOString(), code: '002594.SZ', name: '比亚迪', side: 'sell', volume: 100, price: 245.6, reason: '止损' },
]

export const getNextSchedule = () => ({
  now: dayjs().format('YYYY-MM-DD HH:mm:ss'),
  nextBuy: '今日 14:50',
  nextSell: '明日 09:30 - 09:59',
  isWeekend: [0, 6].includes(dayjs().day()),
})

export const getCandidates = () => [
  { code: '600519.SH', name: '贵州茅台', price: 1720.5, rise: 2.1, moneyFlow: 120000000, volRatio: 2.1, turn: 5.2 },
  { code: '000858.SZ', name: '五粮液', price: 148.8, rise: 1.8, moneyFlow: 85000000, volRatio: 1.9, turn: 4.8 },
]

export const getEquityCurve = () => [
  { date: dayjs().subtract(6, 'day').format('MM/DD'), total: 122000 },
  { date: dayjs().subtract(5, 'day').format('MM/DD'), total: 123500 },
  { date: dayjs().subtract(4, 'day').format('MM/DD'), total: 125200 },
  { date: dayjs().subtract(3, 'day').format('MM/DD'), total: 124800 },
  { date: dayjs().subtract(2, 'day').format('MM/DD'), total: 126100 },
  { date: dayjs().subtract(1, 'day').format('MM/DD'), total: 127300 },
  { date: dayjs().format('MM/DD'), total: 128560 },
]
