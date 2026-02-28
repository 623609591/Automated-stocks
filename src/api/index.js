/**
 * 数据接口 - 请求 Python 后端 API，未配置后端时回退到本地 mock
 */
import {
  getConnectionStatus,
  getAccountOverview,
  getMarketEnv,
  getStrategyParams,
  getHoldings,
  getTradeHistory,
  getNextSchedule,
  getCandidates,
  getEquityCurve,
} from './mockData'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === '1' || import.meta.env.VITE_USE_MOCK === 'true'

async function get(path) {
  const url = `${BASE}${path}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url} ${res.status}`)
  return res.json()
}

async function fetchOrMock(fn, path) {
  if (USE_MOCK) return fn()
  try {
    return await get(path)
  } catch (e) {
    console.warn('后端 API 请求失败，使用 mock 数据:', e?.message)
    return fn()
  }
}

export async function fetchConnectionStatus() {
  return fetchOrMock(getConnectionStatus, '/api/connection')
}

export async function fetchAccountOverview() {
  return fetchOrMock(getAccountOverview, '/api/account')
}

export async function fetchMarketEnv() {
  return fetchOrMock(getMarketEnv, '/api/market_env')
}

export async function fetchStrategyParams() {
  return fetchOrMock(getStrategyParams, '/api/strategy_params')
}

export async function fetchHoldings() {
  return fetchOrMock(getHoldings, '/api/holdings')
}

export async function fetchTradeHistory() {
  return fetchOrMock(getTradeHistory, '/api/trades')
}

export async function fetchNextSchedule() {
  return fetchOrMock(getNextSchedule, '/api/schedule')
}

export async function fetchCandidates() {
  return fetchOrMock(getCandidates, '/api/candidates')
}

export async function fetchEquityCurve() {
  return fetchOrMock(getEquityCurve, '/api/equity')
}
