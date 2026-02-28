import React from 'react'
import './Card.css'

export default function StrategyParams({ data }) {
  if (!data) return null
  return (
    <div className="card card-wide">
      <h3 className="card-title">策略参数</h3>
      <div className="params-grid">
        <div className="param-item"><span className="label">绿灯仓位</span><span>{(data.maxPositionGreen * 100).toFixed(0)}%</span></div>
        <div className="param-item"><span className="label">黄灯仓位</span><span>{(data.maxPositionYellow * 100).toFixed(0)}%</span></div>
        <div className="param-item"><span className="label">最大持股数</span><span>{data.maxStocks}</span></div>
        <div className="param-item"><span className="label">单日亏损停手</span><span>{(data.maxDailyLossRatio * 100).toFixed(0)}%</span></div>
        <div className="param-item"><span className="label">买入时间</span><span>{data.buyTime}</span></div>
        <div className="param-item"><span className="label">卖出时段</span><span>{data.sellStart} - {data.sellEnd}</span></div>
        <div className="param-item"><span className="label">止盈</span><span className="text-green">≥{data.takeProfit}%</span></div>
        <div className="param-item"><span className="label">止损</span><span className="text-red">≤{data.stopLoss}%</span></div>
        <div className="param-item"><span className="label">选股价格</span><span>{data.minPrice} - {data.maxPrice} 元</span></div>
        <div className="param-item"><span className="label">选股涨跌幅</span><span>{data.minRise}% - {data.maxRise}%</span></div>
      </div>
    </div>
  )
}
