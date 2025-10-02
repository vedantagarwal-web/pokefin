# 🚀 AlphaWealth Setup Guide

Complete setup instructions to get your trillion-dollar AI wealth manager running!

---

## 📋 Prerequisites

### Required Software
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** (optional) — For version control

### Required API Keys
- **OpenAI API Key** — [Get it here](https://platform.openai.com/api-keys)
  - Cost: ~$0.01-0.05 per conversation
  - Models used: GPT-4o for orchestration, GPT-4o-mini for specialist agents

### Optional API Keys (System works without these)
- **Financial Datasets AI** — [Get it here](https://financialdatasets.ai/)
  - Free tier available
  - Used for: Real stock prices, financials, SEC filings
  - Fallback: Mock data if not provided

- **Exa AI** — [Get it here](https://exa.ai/)
  - Free tier available  
  - Used for: Semantic search, news, sentiment analysis
  - Fallback: Mock data if not provided

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Navigate to Project
```bash
cd /Users/vedant/Desktop/pokefin
```

### Step 2: Configure API Keys
```bash
# Copy the example environment file
cp python_backend/.env.example python_backend/.env

# Open the file in your editor
nano python_backend/.env
# or
code python_backend/.env
# or
open -e python_backend/.env
```

**Add your OpenAI API key:**
```bash
OPENAI_API_KEY=sk-your-actual-key-here

# Optional: Add these if you have them
FINANCIAL_DATASETS_API_KEY=your_key_here
EXA_API_KEY=your_key_here
```

Save and close the file.

### Step 3: Start the System
```bash
./start-full-system.sh
```

**What this does:**
1. Checks for `.env` file
2. Creates Python virtual environment
3. Installs Python dependencies
4. Starts Node.js server (port 8787)
5. Starts Python backend (port 8788)

### Step 4: Open in Browser
Open **http://localhost:8787** in your browser

You should see the AlphaWealth chat interface!

---

## 🧪 Test the System

Try these queries to test everything:

```
1. "What's Nvidia's stock price?"
   → Tests: Ticker resolution, price lookup, chart generation

2. "What's the mood in markets today?"
   → Tests: Market overview, sentiment analysis, sector performance

3. "ETFs for Indian stocks"
   → Tests: Search functionality, Exa AI integration

4. "Should I buy TSLA?"
   → Tests: Full multi-agent analysis, all specialist agents

5. "Compare NVDA vs AMD"
   → Tests: Comparison tools, chart generation

6. "What are REITs?"
   → Tests: Research tools, educational content
```

---

## 🔧 Manual Setup (If Automatic Fails)

### Backend Setup

1. **Create virtual environment:**
```bash
cd python_backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Start backend:**
```bash
python main.py
```

Backend should start on **http://localhost:8788**

### Frontend Setup

1. **In a new terminal:**
```bash
cd /Users/vedant/Desktop/pokefin
node server/index.js
```

Frontend should start on **http://localhost:8787**

---

## 🐛 Troubleshooting

### "Python backend unavailable"
**Problem:** Frontend can't reach Python backend

**Solutions:**
1. Make sure Python backend is running (check terminal)
2. Verify it's on port 8788: `curl http://localhost:8788/health`
3. Check for port conflicts: `lsof -i :8788`

### "OpenAI API error"
**Problem:** Invalid or missing API key

**Solutions:**
1. Check `.env` file has correct `OPENAI_API_KEY`
2. Verify key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
3. Make sure there are no extra spaces or quotes in the key
4. Restart the backend after updating `.env`

### "Module not found" errors
**Problem:** Python dependencies not installed

**Solutions:**
```bash
cd python_backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Port Already in Use
**Problem:** Port 8787 or 8788 is already taken

**Solutions:**
```bash
# Find what's using the port
lsof -i :8787
lsof -i :8788

# Kill the process or change the port
# For frontend: PORT=8080 node server/index.js
# For backend: Edit python_backend/.env and change PORT=8788
```

### Virtual Environment Issues
**Problem:** `venv` command not found

**Solutions:**
```bash
# On macOS/Linux
python3 -m pip install virtualenv
python3 -m virtualenv venv

# On Windows
py -m pip install virtualenv
py -m virtualenv venv
```

---

## 📊 Verify Installation

### Check Backend Status
```bash
# Health check
curl http://localhost:8788/health

# Should return:
# {"status":"healthy","timestamp":"2024-01-01T..."}

# Test API
curl http://localhost:8788/api/v2/price/AAPL

# Should return price data for Apple stock
```

### Check Frontend Status
```bash
curl http://localhost:8787

# Should return HTML of the chat interface
```

### Check API Documentation
Open http://localhost:8788/docs in your browser
You should see FastAPI's interactive API documentation

---

## 🎯 Next Steps

### After Setup
1. **Try the example queries** (see Test the System section)
2. **Explore the API docs** at http://localhost:8788/docs
3. **Check the system logs** in your terminal
4. **Read the architecture** in README.md

### Start Building
1. **Add your API keys** for Financial Datasets AI and Exa AI
2. **Modify agent prompts** in `python_backend/agents/interaction_agent.py`
3. **Add new tools** in `python_backend/agents/tools/`
4. **Customize the UI** in `index.html` and `styles.css`

### Going to Production
1. **Add authentication** (JWT, OAuth)
2. **Add database** (PostgreSQL)
3. **Add caching** (Redis)
4. **Deploy backend** (AWS, GCP, or Heroku)
5. **Deploy frontend** (Vercel, Netlify)

---

## 💰 Cost Estimates

### Development (Testing)
- **OpenAI API**: $5-20/month
- **Financial Datasets AI**: Free tier (5k requests/month)
- **Exa AI**: Free tier (1k searches/month)

**Total: ~$5-20/month**

### Production (100 users)
- **OpenAI API**: $100-500/month
- **Financial Datasets AI**: $50-200/month
- **Exa AI**: $50-200/month
- **Infrastructure**: $50-100/month

**Total: ~$250-1000/month**

---

## 📚 Additional Resources

- **Main README**: `README.md` — Complete project overview
- **API Documentation**: http://localhost:8788/docs — Interactive API docs
- **OpenPoke Architecture**: `vendor/OpenPoke/` — Multi-agent inspiration
- **TradingAgents Paper**: [ArXiv](https://arxiv.org/abs/2412.20138)

---

## 🆘 Get Help

If you're stuck:

1. **Check the logs** in your terminal
2. **Read error messages** carefully
3. **Try the troubleshooting section** above
4. **Check API key validity**
5. **Restart both services**

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] OpenAI API key obtained
- [ ] `.env` file configured
- [ ] Python dependencies installed
- [ ] Backend starts successfully (port 8788)
- [ ] Frontend starts successfully (port 8787)
- [ ] Can see chat interface in browser
- [ ] Test query "What's NVDA?" works
- [ ] See response from AI agent

**All checked?** You're ready to build the world's best AI wealth manager! 🚀

---

**Questions?** This is a learning project. Experiment, break things, and learn!

