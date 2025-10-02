# 🚀 AlphaWealth

**The World's Best AI Financial Wealth Manager**

AlphaWealth is a truly agentic AI system that helps users make better investment decisions through:
- **Multi-agent orchestration** (inspired by OpenPoke + TradingAgents)
- **Dynamic tool selection** (LLM decides what to do, no hardcoded routing)
- **Comprehensive analysis** (fundamental, technical, sentiment, risk)
- **Beautiful visualizations** (embedded TradingView charts)
- **Conversational interface** (Sydney personality - knowledgeable but never boring)

---

## ⚡ Quick Start

### Prerequisites
- **Node.js 18+** (for frontend server)
- **Python 3.10+** (for AI backend)
- **OpenAI API Key** (required)
- **Financial Datasets AI API Key** (optional, will use mock data)
- **Exa AI API Key** (optional, will use mock data)

### Installation

1. **Clone and navigate to the project:**
```bash
cd /Users/vedant/Desktop/pokefin
```

2. **Set up API keys:**
```bash
# Copy the example env file
cp python_backend/.env.example python_backend/.env

# Edit python_backend/.env and add your keys:
# - OPENAI_API_KEY=your_key_here (REQUIRED)
# - FINANCIAL_DATASETS_API_KEY=your_key_here (optional)
# - EXA_API_KEY=your_key_here (optional)
```

3. **Start the full system:**
```bash
./start-full-system.sh
```

That's it! Open **http://localhost:8787** in your browser.

---

## 🎯 What You Can Do

### Ask Anything Financial

```
"What's Nvidia's stock price?"
"Should I buy TSLA?"
"What's the mood in markets today?"
"ETFs for Indian stocks"
"Compare NVDA vs AMD"
"What are REITs?"
"Analyze my portfolio"
```

The system uses **OpenAI function calling** to dynamically decide:
- What data to fetch
- Which specialist agents to invoke
- What analysis to perform
- What charts to show

No hardcoded routing - truly agentic! 🤖

---

## 🏗️ Architecture

### Frontend (Node.js - Port 8787)
- `index.html` — Clean iMessage-style chat UI
- `styles.css` — Beautiful, modern styling
- `js/app.js` — Chat logic with chart embedding
- `server/index.js` — Static file server + original simple chat API

### Backend (Python FastAPI - Port 8788)
- **Interaction Agent** — Conversational orchestrator (uses GPT-4o)
- **Specialist Agents** — Fundamental, Technical, Sentiment, Risk analysis
- **Tool System** — Dynamic function calling for any query type
- **Services** — Financial Datasets AI, Exa AI, Chart generation

### Data Flow
```
User Query
    ↓
Interaction Agent (GPT-4o with function calling)
    ↓
Tool Executor (parallel execution)
    ↓
Specialist Agents (if deep analysis needed)
    ↓
Response Synthesis + Charts
    ↓
Beautiful UI with embedded visualizations
```

---

## 📁 Project Structure

```
pokefin/
├── index.html                    # Frontend UI
├── styles.css                    # Styling
├── js/
│   ├── app.js                   # Chat logic
│   └── agents.js                # (legacy)
├── server/
│   └── index.js                 # Node.js server
├── python_backend/              # AI System
│   ├── main.py                  # FastAPI app
│   ├── requirements.txt         # Python dependencies
│   ├── agents/
│   │   ├── system.py           # Main orchestrator
│   │   ├── interaction_agent.py # Conversational agent
│   │   ├── specialist_agents.py # Analysis agents
│   │   ├── chart_agent.py      # Chart generation
│   │   └── tools/              # Tool registry & implementations
│   └── services/
│       ├── financial_datasets_client.py
│       ├── exa_client.py
│       └── ticker_resolver.py
├── start-full-system.sh         # Start everything
└── README.md                    # This file
```

---

## 🔧 Development

### Start Services Individually

**Frontend only:**
```bash
node server/index.js
# Opens on http://localhost:8787
```

**Backend only:**
```bash
cd python_backend
./start.sh
# Opens on http://localhost:8788
# API docs: http://localhost:8788/docs
```

### API Endpoints

- `POST /api/v2/chat` — Main chat endpoint
- `POST /api/v2/chart` — Get chart data
- `GET /api/v2/price/{ticker}` — Quick price lookup
- `GET /api/v2/market/overview` — Market overview
- `WS /ws/chat/{session_id}` — WebSocket for streaming

---

## 🎨 Key Features

### ✅ Implemented
- ✅ Multi-agent system with OpenAI function calling
- ✅ Dynamic tool selection (no hardcoded routing)
- ✅ Company name → ticker resolution
- ✅ Real-time stock prices (with fallback to mock data)
- ✅ Market overview & sentiment
- ✅ Stock search by criteria
- ✅ Chart generation for visualization
- ✅ Beautiful chat UI with Sydney personality
- ✅ Session management
- ✅ Comprehensive error handling

### 🚧 Next Phase (Weeks 3-6)
- 🚧 Full fundamental analysis (DCF, ratios, financials)
- 🚧 Advanced technical indicators (RSI, MACD, patterns)
- 🚧 Real sentiment analysis with Exa AI
- 🚧 Portfolio management & tracking
- 🚧 Whiteboard view (detailed analysis)
- 🚧 TradingView Lightweight Charts integration
- 🚧 User authentication
- 🚧 Database (PostgreSQL)

### 🎯 Future Phases
- AI hedge fund
- Execution capabilities (paper + real trading)
- Social features & leaderboard
- Embedded finance (credit card, banking)
- B2B institutional product
- Global expansion

---

## 💡 Usage Examples

### Simple Price Check
**You:** "What's Nvidia's stock price?"

**AlphaWealth:** "NVDA is trading at $875, up $12 (1.4%) today. The stock's been on a nice run this week. Want me to dig deeper?"

### Deep Analysis
**You:** "Should I buy TSLA?"

**AlphaWealth:** *[Runs multi-agent analysis in parallel]*

"Here's my analysis on TSLA:

**Fundamentals (6/10):** Valuation stretched at 65x P/E, but margins strong.
**Technical (7/10):** Uptrend intact, RSI cooling from overbought.
**Sentiment (8/10):** Very bullish - institutional buying up 12%.

**Recommendation:** 🟡 HOLD or small position if you believe in the story.

[📊 Open Whiteboard for full analysis]"

### Market Overview
**You:** "What's the mood in markets today?"

**AlphaWealth:** "Markets are cautiously optimistic 🟢

S&P +0.3%, Nasdaq +0.7%, Dow -0.1%

Tech is leading (+1.2%) on AI demand. Energy down (-0.8%) on oil concerns.
Overall sentiment: Moderately Bullish"

---

## 🔑 API Keys

### OpenAI (Required)
Get from: https://platform.openai.com/api-keys
Cost: ~$0.01-0.05 per conversation

### Financial Datasets AI (Optional)
Get from: https://financialdatasets.ai/
Free tier available
Fallback: System uses mock data if not provided

### Exa AI (Optional)
Get from: https://exa.ai/
Free tier available
Fallback: System uses mock data if not provided

---

## 🚀 Path to $1T Company

This is the foundation. Next phases include:
1. **Portfolio Management** — Track & optimize user portfolios
2. **Execution** — Paper trading → real trades
3. **Social Features** — Leaderboard, copy trading, viral loops
4. **AI Hedge Fund** — Pooled fund managed by AI
5. **Embedded Finance** — Credit cards, banking, lending
6. **B2B Product** — Sell to RIAs, hedge funds, institutions
7. **Global Expansion** — India, Europe, Asia markets

---

## ⚠️ Disclaimer

This is an educational prototype for research purposes. Not financial advice.
Never invest money you can't afford to lose. Past performance doesn't guarantee future results.

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

Built by Vedant. Want to contribute? This is a learning project - feel free to fork and experiment!

---

**Let's build the world's best AI wealth manager! 🚀**
