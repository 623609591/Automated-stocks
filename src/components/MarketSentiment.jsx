import React from 'react'
import './Card.css'

/** 与 QMT 策略市场情绪三档一致：昨日涨停股今日平均涨跌 */
const SENTIMENT_STYLE = {
  '情绪高涨': { color: 'var(--green)', icon: '🔥', desc: '昨日涨停股今日平均涨幅 ≥2%' },
  '情绪正常': { color: 'var(--text)', icon: '➖', desc: '-1% ≤ 平均涨跌 < 2%' },
  '情绪冰点': { color: 'var(--red)', icon: '❄️', desc: '昨日涨停股今日平均跌幅 ≤-1%' },
}

export default function MarketSentiment({ data }) {
  if (!data) return null
  const { label, avgChange } = data
  const style = SENTIMENT_STYLE[label] || SENTIMENT_STYLE['情绪正常']
  return (
    <div className="card">
      <h3 className="card-title">市场情绪</h3>
      <div className="signal-box" style={{ borderColor: style.color }}>
        <span className="signal-icon">{style.icon}</span>
        <div>
          <div className="signal-label">{label}</div>
          <div className="signal-desc">{style.desc}</div>
        </div>
      </div>
      <div className="env-stats">
        <div className="env-row">
          <span className="label">昨日涨停股今日平均涨跌</span>
          <span className={avgChange != null ? (avgChange >= 0 ? 'text-red' : 'text-green') : ''}>
            {avgChange != null ? `${avgChange >= 0 ? '+' : ''}${avgChange}%` : '-'}
          </span>
        </div>
      </div>
    </div>
  )
}
