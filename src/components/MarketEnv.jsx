import React from 'react'
import './Card.css'

// 与 QMT.py 大盘环境 6 档信号一致（当前策略仓位：红灯0%、普通黄灯20%、强黄灯50%、普通绿灯70%、强绿灯75%、超强绿灯85%）
const SIGNAL_MAP = {
  RED: { label: '红灯', desc: '空仓不买', color: 'var(--red)', icon: '🔴' },
  YELLOW: { label: '普通黄灯', desc: '20% 仓位', color: 'var(--yellow)', icon: '🟡' },
  STRONG_YELLOW: { label: '强黄灯', desc: '50% 仓位', color: 'var(--yellow)', icon: '🟡' },
  GREEN: { label: '普通绿灯', desc: '70% 仓位', color: 'var(--green)', icon: '🟢' },
  STRONG_GREEN: { label: '强绿灯', desc: '75% 仓位', color: 'var(--green)', icon: '🟢' },
  SUPER_GREEN: { label: '超强绿灯', desc: '85% 仓位', color: 'var(--green)', icon: '🟢' },
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
          <span>{shIndex != null && shIndex !== 0 ? shIndex.toFixed(2) : '-'}</span>
        </div>
        <div className="env-row">
          <span className="label">MA20</span>
          <span>{shMa20 != null && shMa20 !== 0 ? shMa20.toFixed(2) : '-'}</span>
        </div>
        <div className="env-row">
          <span className="label">今日涨跌幅</span>
          <span className={shTodayReturn != null ? (shTodayReturn >= 0 ? 'text-red' : 'text-green') : ''}>
            {shTodayReturn != null ? `${shTodayReturn >= 0 ? '+' : ''}${shTodayReturn.toFixed(2)}%` : '-'}
          </span>
        </div>
        <div className="env-row">
          <span className="label">近10日下跌天数</span>
          <span>{dropDaysIn10 != null ? dropDaysIn10 : '-'}</span>
        </div>
      </div>
    </div>
  )
}
