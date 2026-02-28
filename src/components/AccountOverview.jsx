import React from 'react'
import './Card.css'

export default function AccountOverview({ data }) {
  if (!data) return null
  const { totalAsset, available, todayPnl, todayPnlRatio, dailyLossLimitHit } = data
  const pnlClass = todayPnl >= 0 ? 'text-green' : 'text-red'
  return (
    <div className="card">
      <h3 className="card-title">账户总览</h3>
      <div className="stat-grid">
        <div className="stat-item">
          <span className="label">总资产</span>
          <span className="stat-value">¥ {(totalAsset || 0).toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="label">可用资金</span>
          <span className="stat-value">¥ {(available || 0).toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="label">当日盈亏</span>
          <span className={`stat-value ${pnlClass}`}>
            ¥ {(todayPnl || 0).toLocaleString()} ({(todayPnlRatio != null ? (todayPnlRatio * 100).toFixed(2) : '0')}%)
          </span>
        </div>
      </div>
      {dailyLossLimitHit && (
        <div className="alert alert-warning">⚠️ 当日亏损已超 2%，已停止买入</div>
      )}
    </div>
  )
}
