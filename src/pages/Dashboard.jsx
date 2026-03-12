import React, { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import ConnectionStatus from '../components/ConnectionStatus'
import AccountOverview from '../components/AccountOverview'
import MarketEnv from '../components/MarketEnv'
import MarketSentiment from '../components/MarketSentiment'
import HoldingsTable from '../components/HoldingsTable'
import * as api from '../api'
import './Dashboard.css'

export default function Dashboard() {
  const [connection, setConnection] = useState(null)
  const [account, setAccount] = useState(null)
  const [marketEnv, setMarketEnv] = useState(null)
  const [marketSentiment, setMarketSentiment] = useState(null)
  const [holdings, setHoldings] = useState(null)
  const [updatedAt, setUpdatedAt] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    try {
      const [meta, conn, acc, env, sentiment, pos] = await Promise.all([
        api.fetchStateMeta(),
        api.fetchConnectionStatus(),
        api.fetchAccountOverview(),
        api.fetchMarketEnv(),
        api.fetchMarketSentiment(),
        api.fetchHoldings(),
      ])
      setUpdatedAt(meta?.updatedAt ?? null)
      setConnection(conn)
      setAccount(acc)
      setMarketEnv(env)
      setMarketSentiment(sentiment)
      setHoldings(pos)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    const t = setInterval(refresh, 10000)
    return () => clearInterval(t)
  }, [])

  const formatUpdatedAt = (s) => {
    if (!s) return '-'
    const d = dayjs(s)
    return d.isValid() ? d.format('YYYY-MM-DD HH:mm:ss') : s
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <span>加载中...</span>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>自动化炒股 · 国金 QMT 策略监控</h1>
        <div className="header-right">
          <span className="updated-at">
            数据有效时间截止到：{updatedAt ? formatUpdatedAt(updatedAt) : '暂无数据'}
          </span>
        </div>
      </header>

      <div className="dashboard-grid">
        <ConnectionStatus data={connection} />
        <AccountOverview data={account} />
        <MarketEnv data={marketEnv} />
        <MarketSentiment data={marketSentiment} />
        <HoldingsTable data={holdings} />
      </div>
    </div>
  )
}
