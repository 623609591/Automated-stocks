import React from 'react'
import './Card.css'

export default function HoldingsTable({ data }) {
  if (!data || !data.length) {
    return (
      <div className="card card-wide">
        <h3 className="card-title">当前持仓</h3>
        <p className="text-muted holdings-empty">暂无持仓</p>
      </div>
    )
  }
  return (
    <div className="card card-wide">
      <h3 className="card-title">当前持仓</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>代码</th>
              <th>名称</th>
              <th>持仓</th>
              <th>成本</th>
              <th>现价</th>
              <th>盈亏比例</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={row.code || i}>
                <td>{row.code}</td>
                <td>{row.name}</td>
                <td>{row.volume}</td>
                <td>{row.costPrice?.toFixed(2)}</td>
                <td>{row.currentPrice?.toFixed(2)}</td>
                <td className={row.pnlRatio >= 0 ? 'text-green' : 'text-red'}>
                  {(row.pnlRatio != null ? row.pnlRatio : 0).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
