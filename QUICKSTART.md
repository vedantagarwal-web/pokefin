# ⚡ AlphaWealth - Quick Start

Get up and running in 60 seconds!

## Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (starts with `sk-...`)

## Step 2: Configure

```bash
cd /Users/vedant/Desktop/pokefin
cp python_backend/.env.example python_backend/.env
```

Edit `python_backend/.env` and add your key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step 3: Start

```bash
./start-full-system.sh
```

## Step 4: Chat!

Open http://localhost:8787

Try: **"What's Nvidia's stock price?"**

---

## 🎉 That's it!

You now have:
- ✅ Multi-agent AI system running
- ✅ Dynamic tool selection
- ✅ Real-time stock data (with fallbacks)
- ✅ Beautiful chat interface
- ✅ Sydney personality

## Next Steps

1. Try more queries (see README.md examples)
2. Add Financial Datasets AI key for real data
3. Add Exa AI key for better search
4. Customize the agents
5. Build the trillion-dollar features!

---

**Stuck?** See SETUP.md for detailed troubleshooting.

