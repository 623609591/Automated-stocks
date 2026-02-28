import React from 'react'
import './Card.css'

export default function NextSchedule({ data }) {
  if (!data) return null
  const { now, nextBuy, nextSell, isWeekend } = data
  return (
    <div className="card">
      <h3 className="card-title">运行节奏</h3>
      <div className="status-row">
        <span className="label">当前时间</span>
        <span>{now}</span>
      </div>
      <div className="status-row">
        <span className="label">下次买入</span>
        <span>{nextBuy}</span>
      </div>
      <div className="status-row">
        <span className="label">下次卖出</span>
        <span>{nextSell}</span>
      </div>
      {isWeekend && <div className="alert alert-info">周末不交易</div>}
    </div>
  )
}
