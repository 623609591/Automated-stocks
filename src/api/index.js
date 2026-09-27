/**
 * 数据接口 - 仅请求后端 API，无 mock。请求失败时返回空数据。
 */
const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function get(path) {
  const url = `${BASE}${path}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url} ${res.status}`)
  return res.json()
}

async function fetchOrEmpty(getEmpty, path) {
  try {
    return await get(path)
  } catch (e) {
    console.warn('后端 API 请求失败，返回空数据:', e?.message)
    return getEmpty()
  }
}

const emptyConnection = () => ({ connected: false, lastHeartbeat: null, accountId: null, qmtHost: null, updatedAt: null })
const emptyAccount = () => ({ totalAsset: 0, available: 0, todayPnl: 0, todayPnlRatio: 0, dailyLossLimitHit: false, updatedAt: null })
const emptyMarketEnv = () => ({ signal: 'YELLOW', shIndex: null, shMa20: null, shTodayReturn: null, dropDaysIn10: null, updatedAt: null })
const emptySchedule = () => ({ now: null, nextBuy: null, nextSell: null, isWeekend: null, updatedAt: null })

export async function fetchStateMeta() {
  return fetchOrEmpty(() => ({ updatedAt: null }), '/api/state_meta')
}

export async function fetchConnectionStatus() {
  return fetchOrEmpty(emptyConnection, '/api/connection')
}

export async function fetchAccountOverview() {
  return fetchOrEmpty(emptyAccount, '/api/account')
}

export async function fetchMarketEnv() {
  return fetchOrEmpty(emptyMarketEnv, '/api/market_env')
}

const emptyMarketSentiment = () => ({ label: '情绪正常', avgChange: 0, updatedAt: null })

export async function fetchMarketSentiment() {
  return fetchOrEmpty(emptyMarketSentiment, '/api/market_sentiment')
}

export async function fetchHoldings() {
  return fetchOrEmpty(() => [], '/api/holdings')
}

export async function fetchNextSchedule() {
  return fetchOrEmpty(emptySchedule, '/api/schedule')
}
