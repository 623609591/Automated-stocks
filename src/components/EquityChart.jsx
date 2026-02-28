import React from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import dayjs from 'dayjs'
import './Card.css'

const mockEquity = [
  { date: dayjs().subtract(6, 'day').format('MM/DD'), total: 122000 },
  { date: dayjs().subtract(5, 'day').format('MM/DD'), total: 123500 },
  { date: dayjs().subtract(4, 'day').format('MM/DD'), total: 125200 },
  { date: dayjs().subtract(3, 'day').format('MM/DD'), total: 124800 },
  { date: dayjs().subtract(2, 'day').format('MM/DD'), total: 126100 },
  { date: dayjs().subtract(1, 'day').format('MM/DD'), total: 127300 },
  { date: dayjs().format('MM/DD'), total: 128560 },
]

export default function EquityChart({ data }) {
  const series = (data && data.length) ? data : mockEquity
  return (
    <div className="card card-wide">
      <h3 className="card-title">资产曲线</h3>
      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer>
          <AreaChart data={series}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--green)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="var(--green)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} />
            <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `¥${(v / 10000).toFixed(1)}万`} />
            <Tooltip
              contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)' }}
              formatter={(v) => [`¥ ${Number(v).toLocaleString()}`, '总资产']}
              labelFormatter={(l) => l}
            />
            <Area type="monotone" dataKey="total" stroke="var(--green)" fill="url(#equityGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
