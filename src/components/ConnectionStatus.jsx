import React from 'react'
import dayjs from 'dayjs'
import './Card.css'

export default function ConnectionStatus({ data }) {
  if (!data) return null
  const { connected, lastHeartbeat, accountId, qmtHost } = data
  return (
    <div className="card">
      <h3 className="card-title">QMT 连接状态</h3>
      <div className="status-row">
        <span className="label">状态</span>
        <span className={`badge ${connected ? 'badge-success' : 'badge-danger'}`}>
          {connected ? '已连接' : '未连接'}
        </span>
      </div>
      <div className="status-row">
        <span className="label">资金账号</span>
        <span>{accountId}</span>
      </div>
      <div className="status-row">
        <span className="label">MiniQMT</span>
        <span className="text-muted">{qmtHost}</span>
      </div>
      <div className="status-row">
        <span className="label">最后心跳</span>
        <span className="text-muted">{dayjs(lastHeartbeat).format('HH:mm:ss')}</span>
      </div>
    </div>
  )
}
