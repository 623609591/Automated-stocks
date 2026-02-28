import React, { useState, useEffect } from 'react'
import ConnectionStatus from '../components/ConnectionStatus'
import AccountOverview from '../components/AccountOverview'
import MarketEnv from '../components/MarketEnv'
import StrategyParams from '../components/StrategyParams'
import HoldingsTable from '../components/HoldingsTable'
import TradeHistory from '../components/TradeHistory'
import NextSchedule from '../components/NextSchedule'
import EquityChart from '../components/EquityChart'
import * as api from '../api'
import './Dashboard.css'

export default function Dashboard() {
  const [connection, setConnection] = useState(null)
  const [account, setAccount] = useState(null)
  const [marketEnv, setMarketEnv] = useState(null)
  const [params, setParams] = useState(null)
  const [holdings, setHoldings] = useState(null)
  const [trades, setTrades] = useState(null)
  const [schedule, setSchedule] = useState(null)
  const [equity, setEquity] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    try {
      const [conn, acc, env, prm, pos, his, sch, eq] = await Promise.all([
        api.fetchConnectionStatus(),
        api.fetchAccountOverview(),
        api.fetchMarketEnv(),
        api.fetchStrategyParams(),
        api.fetchHoldings(),
        api.fetchTradeHistory(),
        api.fetchNextSchedule(),
        api.fetchEquityCurve(),
      ])
      setConnection(conn)
      setAccount(acc)
      setMarketEnv(env)
      setParams(prm)
      setHoldings(pos)
      setTrades(his)
      setSchedule(sch)
      setEquity(eq)
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
        <button className="btn-refresh" onClick={refresh}>刷新</button>
      </header>

      <div className="dashboard-grid">
        <ConnectionStatus data={connection} />
        <AccountOverview data={account} />
        <MarketEnv data={marketEnv} />
        <NextSchedule data={schedule} />
        <StrategyParams data={params} />
        <HoldingsTable data={holdings} />
        <TradeHistory data={trades} />
        <EquityChart data={equity} />
      </div>
    </div>
  )
}
