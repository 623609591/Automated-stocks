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

## 页面展示的数据（与策略状态文件一致）

| 模块 | 说明 |
|------|------|
| **QMT 连接状态** | 是否连接、资金账号、交易端、最后心跳 |
| **账户总览** | 总资产、可用资金、当日盈亏、单日亏 2% 停手 |
| **大盘环境** | 红/黄/绿信号、上证收盘、MA20、今日涨跌幅、近 10 日下跌天数（无数据时显示 -） |
| **运行节奏** | 当前时间、下次买入、下次卖出、是否周末 |
| **策略参数** | 仓位梯度、买卖时间、止盈止损、选股条件等 |
| **当前持仓** | 代码、名称、持仓量、成本、现价、盈亏比例 |

（最近交易、候选标的、资产曲线当前策略未上报，前端已不展示。）

## 本地运行（前后端一起）

### 1. 后端（Python）

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或双击 `backend/启动后端.bat`。API 文档：http://localhost:8000/docs

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

## 策略在 QMT 交易端里跑，项目只读文件

**策略始终在 QMT 交易端里运行**，不在你项目里启动；你的项目只做一件事：**读策略写出的状态文件**，给监控大屏用。

1. **QMT 里**：你照常在交易端里运行策略（`QMT.py`）。策略会把自己的状态（账户、持仓、大盘等）写到一个 **JSON 文件**里。
2. **你项目里**：只启动 **后端** 和 **前端**。后端会去 **读这个 JSON 文件**；有且没过期就返回给大屏，没有或过期就回退 mock。
3. **要一致的一点**：策略「往哪写」和项目「从哪读」必须是 **同一个文件的路径**（默认都是 `backend/strategy_state.json`）。

### 你需要做的

- **策略在 QMT 里要知道「写到哪里」**  
  QMT 下无 `__file__` 时，`QMT.py` 里已写死默认路径 `d:\Automated-stocks\backend\strategy_state.json`（可按你本机改）。若需用别的路径，在系统环境变量里设 `DASHBOARD_STATE_PATH` 即可。

- **项目这边**  
  先启动 **后端**（`cd backend` 后 `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`，或双击 `backend/启动后端.bat`），再 **前端**（`npm run dev`）。后端会读 `backend/strategy_state.json`。

### 运行顺序（总结）

1. 在 **QMT 交易端里** 运行策略。
2. 在 **项目里** 启动后端、再启动前端，打开监控大屏即可看到策略状态。

---

## 对接真实 QMT（旧方式说明）

当前后端**优先从状态文件读取**（见上）；无状态文件或已过期时使用 `backend/mock_data.py` 的模拟数据。若你改为在策略层直接对接 QMT API（不通过状态文件），可在 **backend/strategy.py** 中实现并保持各接口 **字段名与类型** 与 `backend/mock_data.py`、`src/api/mockData.js` 一致。

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
