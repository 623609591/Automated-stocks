import React from 'react'
import './Card.css'

const SIGNAL_MAP = {
  RED: { label: '红灯', desc: '空仓不买', color: 'var(--red)', icon: '🔴' },
  YELLOW: { label: '黄灯', desc: '40% 仓位', color: 'var(--yellow)', icon: '🟡' },
  GREEN: { label: '绿灯', desc: '60% 仓位', color: 'var(--green)', icon: '🟢' },
}

export default function MarketEnv({ data }) {
  if (!data) return null
  const { signal, shIndex, shMa20, shTodayReturn, dropDaysIn10 } = data
  const info = SIGNAL_MAP[signal] || SIGNAL_MAP.YELLOW
  return (
    <div className="card">
      <h3 className="card-title">大盘环境（上证）</h3>
      <div className="signal-box" style={{ borderColor: info.color }}>
        <span className="signal-icon">{info.icon}</span>
        <div>
          <div className="signal-label">{info.label}</div>
          <div className="signal-desc">{info.desc}</div>
        </div>
      </div>
      <div className="env-stats">
        <div className="env-row">
          <span className="label">指数收盘</span>
          <span>{shIndex != null ? shIndex.toFixed(2) : '-'}</span>
        </div>
        <div className="env-row">
          <span className="label">MA20</span>
          <span>{shMa20 != null ? shMa20.toFixed(2) : '-'}</span>
        </div>
        <div className="env-row">
          <span className="label">今日涨跌幅</span>
          <span className={shTodayReturn >= 0 ? 'text-green' : 'text-red'}>
            {shTodayReturn != null ? `${shTodayReturn >= 0 ? '+' : ''}${shTodayReturn.toFixed(2)}%` : '-'}
          </span>
        </div>
        <div className="env-row">
          <span className="label">近10日下跌天数</span>
          <span>{dropDaysIn10 ?? '-'}</span>
        </div>
      </div>
    </div>
  )
}
