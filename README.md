# ⊥ Orthogonal

**Institutional-Grade AI Research Terminal**

Multi-agent AI system that thinks like a hedge fund research team. Deep equity analysis. Bloomberg-level data. In seconds.

---

## 🎯 What Is Orthogonal?

Orthogonal is an AI-powered equity research platform that uses a multi-agent debate system to analyze stocks. Unlike single-LLM tools, Orthogonal deploys specialized AI analysts that debate every investment decision:

- **Fundamental Analyst** → Financial statements, valuations, growth metrics
- **Technical Analyst** → Price action, volume, support/resistance
- **Sentiment Analyst** → Social media, news, Reddit, Twitter
- **Risk Analyst** → Valuation risk, volatility, market conditions

Every recommendation comes with a conviction score (1-10), full debate transcript, and transparent sourcing.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Backend (Python)
cd python_backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (Node.js)
cd ../server
npm install
```

### 2. Configure API Keys

Create `python_backend/.env`:

```env
# Required
OPENAI_API_KEY=sk-...
FDS_API_KEY=...  # Financial Datasets AI
EXA_API_KEY=...  # Exa AI

# Optional
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=...
```

### 3. Launch

```bash
# Start backend
cd python_backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8788

# Start frontend (new terminal)
cd server
node index.js
```

Then visit: **http://localhost:8787**

---

## 💼 Features

### Multi-Agent Debate System
Every stock is analyzed by specialized AI agents that debate the investment case. Bull vs Bear. Just like a real hedge fund research meeting.

### Bloomberg-Level Data
- Real-time prices & fundamentals (Financial Datasets AI)
- SEC filings, earnings materials, institutional positions (Exa AI)
- Social sentiment (Reddit, Twitter)
- Insider trades, 13F filings, options flow

### Research Whiteboard
Bloomberg terminal-style interface with:
- Full financial statements
- Peer comparison tables
- Complete debate transcript
- Risk assessment
- Direct links to SEC filings

### Transparent Sourcing
Every data point is cited. Direct links to:
- SEC filings (10-K, 10-Q, 8-K, proxies)
- Institutional positions (WhaleWisdom, 13F)
- Earnings materials
- News articles

---

## 🎨 Design Philosophy

**"Independent. Contrarian. Orthogonal."**

- **Minimalist** — Apple-inspired design. Black, white, silver, ocean blue.
- **Professional** — Bloomberg terminal aesthetic. Data-first.
- **Transparent** — Show your work. Cite every source.
- **Honest** — Show both bull and bear cases. Acknowledge uncertainty.

---

## 📊 Example Usage

```
You: "Should I buy Tesla?"

Orthogonal: 
🎯 Recommendation: SELL
Conviction: 2/10 ⭐⭐
Price: $436 → $370.60 (-15%)

💡 Key Thesis:
The increasing competition from major automakers and the potential 
for a saturated EV market could significantly threaten Tesla's market 
share and profit margins.

📊 Market Data:
• P/E Ratio: 302.78x (EXTREME valuation risk)
• Profit Margin: 5.21%
• Market Cap: $1.53T

📱 Social Sentiment:
• Reddit: BEARISH (33% bullish)
• Twitter: VERY BULLISH (75% bullish)

⚖️ Bull Case: Strong brand loyalty, innovation leadership...
⚠️ Bear Case: Extreme valuation, intensifying competition...

📋 [View Full Research Whiteboard →]
```

---

## 🧠 Architecture

### Backend (Python + FastAPI)
- **InteractionAgent** (GPT-4o) → Orchestrator, understands user queries
- **Specialist Agents** → Fundamental, Technical, Sentiment, Risk
- **ResearchCoordinator** → Deep research with debate system
- **DebateCoordinator** → Bull vs Bear multi-round debates
- **Tool Executors** → 10+ data sources, parallel execution

### Frontend (Node.js + Vanilla JS)
- **Landing Page** → Professional, Apple-inspired
- **Chat Terminal** → Bloomberg-style research interface
- **Research Whiteboard** → Comprehensive analysis view
- **TradingView Integration** → Interactive charts

### Data Sources
1. Financial Datasets AI → Real-time prices, financials
2. Exa AI → SEC filings, institutional positions, earnings
3. Reddit API → r/wallstreetbets, r/stocks sentiment
4. Twitter API → FinTwit sentiment
5. Internal calculations → P/E, margins, growth rates

---

## 🔧 Tech Stack

**Backend:**
- Python 3.12
- FastAPI (async web framework)
- OpenAI GPT-4o & o1-preview (multi-agent system)
- Financial Datasets AI (market data)
- Exa AI (semantic search, SEC filings)

**Frontend:**
- Node.js + Express
- Vanilla JavaScript (no framework bloat)
- TradingView Widgets
- CSS Variables (Apple/Bloomberg aesthetic)

**Infrastructure:**
- In-memory research storage (migrating to Supabase)
- Real-time WebSocket updates
- Parallel tool execution

---

## 📚 Project Structure

```
orthogonal/
├── index.html              # Landing page
├── chat.html               # Research terminal
├── whiteboard.html         # Bloomberg-style research view
├── styles.css              # Professional Apple/Bloomberg theme
├── js/
│   ├── app.js              # Chat logic
│   └── charts.js           # TradingView integration
├── python_backend/
│   ├── main.py             # FastAPI app
│   ├── agents/
│   │   ├── interaction_agent.py      # GPT-4o orchestrator
│   │   ├── debate_coordinator.py     # Bull vs Bear system
│   │   ├── research_coordinator.py   # Deep research
│   │   └── tools/
│   │       ├── implementations.py    # 10+ tools
│   │       └── registry.py           # Tool schemas
│   └── services/
│       ├── financial_datasets_client.py
│       └── exa_client.py
└── server/
    └── index.js            # Node.js frontend server
```

---

## 🎯 Roadmap

### ✅ Phase 1: Core Platform (DONE)
- Multi-agent debate system
- 10 data sources integrated
- Research whiteboard
- Professional UI redesign

### 🔄 Phase 2: Data & Charts (IN PROGRESS)
- [ ] Historical charts (5Y price/revenue/earnings)
- [ ] Full balance sheet & cash flow statements
- [ ] Earnings call transcript highlights

### 📋 Phase 3: Authentication & User Management
- [ ] Supabase integration
- [ ] User accounts & saved research
- [ ] Research history
- [ ] Portfolio tracking

### 🚀 Phase 4: Advanced Features
- [ ] Real-time alerts
- [ ] Custom watchlists
- [ ] Earnings call summaries with key quotes
- [ ] Automated research updates

---

## ⚠️ Important Notes

### This Is NOT Financial Advice
Orthogonal is a research tool for educational purposes. We provide analysis and insights, but you should:
- Do your own due diligence
- Consult a licensed financial advisor
- Never invest money you can't afford to lose
- Understand that past performance ≠ future results

### Data Accuracy
We use institutional-grade data sources (Financial Datasets AI, Exa AI), but:
- Data may have delays or errors
- APIs can fail or return incomplete data
- Always verify critical information

### LLM Limitations
Our AI agents are sophisticated but not perfect:
- Can make reasoning errors
- May miss important context
- Should be used as a research assistant, not oracle

---

## 🤝 Contributing

Interested in contributing? We're looking for:
- Data source integrations
- UI/UX improvements
- Bug fixes & performance optimization
- Documentation

Email: hello@orthogonal.ai

---

## 📄 License

MIT License - See LICENSE file for details

---

## 💙 Made with Love in Berkeley, CA

Built by a team that believes:
- Retail investors deserve institutional-grade tools
- AI should augment human judgment, not replace it
- Transparency beats black boxes
- Good design matters

---

**⊥ Orthogonal** — Independent. Contrarian. Orthogonal.

Visit: [orthogonal.ai](https://orthogonal.ai)
