# Automated-stocks 前后端一体

国金佣金宝 QMT 自动化炒股策略的可视化监控：**前端 React + 后端 Python FastAPI**，数据结构前后端一致。

## 项目结构

```
Automated-stocks/
├── backend/                 # Python 后端
│   ├── main.py              # FastAPI 入口与路由
│   ├── strategy.py          # 策略层（对接 QMT 时在此实现）
│   ├── mock_data.py         # 模拟数据（与前端 mockData.js 一致）
│   └── requirements.txt
├── src/                     # React 前端
│   ├── api/index.js         # 请求后端 API，失败时回退 mock
│   ├── api/mockData.js      # 前端 mock（与后端 mock_data 一致）
│   ├── pages/Dashboard.jsx
│   └── components/          # 各监控模块
└── package.json
```

## 页面展示的数据（与 Python 策略对应）

| 模块 | 说明 |
|------|------|
| **QMT 连接状态** | 是否连接 MiniQMT、资金账号、最后心跳 |
| **账户总览** | 总资产、可用资金、当日盈亏、是否触发单日亏 2% 停手 |
| **大盘环境** | 红灯/黄灯/绿灯、上证收盘、MA20、今日涨跌幅、近 10 日下跌天数 |
| **策略参数** | 仓位比例、买卖时间、止盈止损、选股条件等 |
| **当前持仓** | 代码、名称、持仓量、成本、现价、盈亏比例 |
| **最近交易** | 时间、代码、方向、数量、价格、原因（止盈/止损/强制卖） |
| **运行节奏** | 当前时间、下次买入(14:50)、下次卖出(09:30-09:59) |
| **资产曲线** | 总资产历史走势图 |

## 本地运行（前后端一起）

### 1. 后端（Python）

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 2. 前端（React）

```bash
cd Automated-stocks
npm install
npm run dev
```

浏览器打开：http://localhost:5174

前端默认请求 `http://localhost:8000`；若后端未启动，会自动回退到本地 mock 数据。

### 仅跑前端（mock 数据）

不启动后端、只用前端 mock 时：

```bash
# 项目根目录创建 .env 或设置环境变量
echo VITE_USE_MOCK=1 > .env
npm run dev
```

### 后端地址不是 8000 时

在项目根目录 `.env` 中设置：

```
VITE_API_BASE=http://你的后端地址:端口
```

## 对接真实 QMT

当前后端使用 `backend/mock_data.py` 的模拟数据。接入国金 QMT 时：

1. 在 **backend/strategy.py** 中实现真实逻辑：连接 MiniQMT、查资金/持仓/成交、算大盘环境与红黄绿灯等。
2. 设置环境变量 `USE_REAL_QMT=1` 再启动后端，使 `strategy.py` 走真实分支。
3. 保持各接口返回的 **字段名与类型** 与 `backend/mock_data.py`（以及前端 `src/api/mockData.js`）一致即可。

后端接口一览：

- `GET /api/connection` — QMT 连接状态  
- `GET /api/account` — 账户总览  
- `GET /api/market_env` — 大盘环境  
- `GET /api/strategy_params` — 策略参数  
- `GET /api/holdings` — 当前持仓  
- `GET /api/trades` — 最近交易  
- `GET /api/schedule` — 下次买卖时间  
- `GET /api/candidates` — 候选标的  
- `GET /api/equity` — 资产曲线数据  

数据结构示例见 `src/api/mockData.js` 与 `backend/mock_data.py`。
