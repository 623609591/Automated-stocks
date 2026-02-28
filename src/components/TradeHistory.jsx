import React from 'react'
import dayjs from 'dayjs'
import './Card.css'

export default function TradeHistory({ data }) {
  if (!data || !data.length) {
    return (
      <div className="card">
        <h3 className="card-title">最近交易</h3>
        <p className="text-muted">暂无记录</p>
      </div>
    )
  }
  return (
    <div className="card card-wide">
      <h3 className="card-title">最近交易</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>代码</th>
              <th>名称</th>
              <th>方向</th>
              <th>数量</th>
              <th>价格</th>
              <th>原因</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td className="text-muted">{dayjs(row.time).format('MM-DD HH:mm')}</td>
                <td>{row.code}</td>
                <td>{row.name}</td>
                <td className={row.side === 'buy' ? 'text-green' : 'text-red'}>{row.side === 'buy' ? '买入' : '卖出'}</td>
                <td>{row.volume}</td>
                <td>{row.price?.toFixed(2)}</td>
                <td>{row.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
