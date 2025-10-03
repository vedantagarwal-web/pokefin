// Minimal chat MVP (frontend) wired to Poke-like backend endpoints

const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('msg');
const sendBtn = document.getElementById('send');
const resetBtn = document.getElementById('resetBtn');

const STORAGE_KEY_BASE = 'pokefin.chat.v1';
const SESSION_KEY = 'pokefin.session.v1';
const API_BASE = '/api/v2';

const sessionId = getSessionId();
const state = {
  messages: load(),
  typingId: null,
};

function storageKey() { return `${STORAGE_KEY_BASE}.${sessionId}`; }

function load() {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return [];
    return JSON.parse(raw);
  } catch { return []; }
}

function save() {
  localStorage.setItem(storageKey(), JSON.stringify(state.messages));
}

function now() { return new Date().toISOString(); }

function addMessage(role, text) {
  const msg = { id: crypto.randomUUID(), role, text, t: now() };
  state.messages.push(msg);
  save();
  renderMessage(msg);
  scrollToBottom();
  return msg;
}

function renderAll() {
  chatEl.innerHTML = '';
  state.messages.forEach(renderMessage);
  scrollToBottom();
}

function linkifyText(text) {
  // Escape HTML to prevent XSS
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  
  // Convert markdown formatting (simplified for browser compatibility)
  let formatted = escaped
    // Bold: **text** (must be converted BEFORE single *)
    .replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
    // Inline code: `text`
    .replace(/`([^`]+?)`/g, '<code style="background: var(--color-surface-elevated); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 13px;">$1</code>');
  
  // Convert URLs to clickable links (styling handled by CSS)
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  const linked = formatted.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Convert newlines to <br>
  return linked.replace(/\n/g, '<br>');
}

function renderMessage(msg) {
  const row = document.createElement('div');
  row.className = `row ${msg.role}`;  // Use 'user' or 'assistant' directly

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = linkifyText(msg.text);
  row.appendChild(bubble);

  // Check if this is a research recommendation (contains "Recommendation:" or "Conviction:")
  if (msg.role === 'assistant' && msg.text && (msg.text.includes('🎯 Recommendation:') || msg.text.includes('Conviction:'))) {
    // Try to extract ticker from message - look for pattern like "TSLA" or "on TSLA"
    const tickerMatch = msg.text.match(/(?:on |research on |deep research on |for )([A-Z]{2,5})\b/i) || msg.text.match(/\b([A-Z]{2,5})\b/);
    if (tickerMatch) {
      const ticker = tickerMatch[1].toUpperCase();
      
      // Parse the research data from the message text
      const researchData = parseResearchData(msg.text, ticker);
      
      // Save research data to localStorage
      localStorage.setItem(`research_${ticker}`, JSON.stringify(researchData));
      localStorage.setItem(`has_research_${ticker}`, 'true');
      
      console.log(`📋 Saved research data for ${ticker}`);
      
      // Add whiteboard button
      const whiteboardBtn = document.createElement('button');
      whiteboardBtn.textContent = '📋 Open Whiteboard';
      whiteboardBtn.className = 'whiteboard-btn';
      whiteboardBtn.onclick = () => window.open(`whiteboard.html?ticker=${ticker}`, '_blank');
      row.appendChild(whiteboardBtn);
    }
  }
  
  function parseResearchData(text, ticker) {
    // Extract key data from the formatted text
    const data = { ticker };
    
    // Extract recommendation
    const recMatch = text.match(/🎯 Recommendation:\s*(\w+)/);
    if (recMatch) data.action = recMatch[1];
    
    // Extract conviction
    const convMatch = text.match(/Conviction:\s*(\d+)\/10/);
    if (convMatch) data.conviction = parseInt(convMatch[1]);
    
    // Extract prices
    const priceMatch = text.match(/Price:\s*\$?([\d.]+)\s*→\s*\$?([\d.]+)\s*\(([+-]?[\d.]+)%\)/);
    if (priceMatch) {
      data.current_price = parseFloat(priceMatch[1]);
      data.target_price = parseFloat(priceMatch[2]);
      data.upside_pct = parseFloat(priceMatch[3]);
    }
    
    // Extract key thesis
    const thesisMatch = text.match(/💡 Key Thesis:\s*([^\n]+)/);
    if (thesisMatch) data.key_thesis = thesisMatch[1];
    
    // Extract data sections with improved regex
    const sections = {
      price_data: {},
      fundamentals: {},
      sentiment_data: {},
      news_headlines: []
    };
    
    // Parse market data
    const marketDataMatch = text.match(/📊 Market Data:[\s\S]*?(?=📊|✅|⚠️|🎯|$)/);
    if (marketDataMatch) {
      const marketText = marketDataMatch[0];
      const priceMatch2 = marketText.match(/Current Price:\s*\$?([\d.,]+)/);
      if (priceMatch2) sections.price_data.current_price = parseFloat(priceMatch2[1].replace(/,/g, ''));
      
      const marketCapMatch = marketText.match(/Market Cap:\s*\$?([\d.]+)([BMT])/);
      if (marketCapMatch) {
        let cap = parseFloat(marketCapMatch[1]);
        const unit = marketCapMatch[2];
        if (unit === 'T') cap *= 1e12;
        else if (unit === 'B') cap *= 1e9;
        else if (unit === 'M') cap *= 1e6;
        sections.price_data.market_cap = cap;
      }
    }
    
    // Parse fundamentals
    const fundMatch = text.match(/P\/E Ratio:\s*([\d.]+)/);
    if (fundMatch) sections.fundamentals.pe_ratio = parseFloat(fundMatch[1]);
    
    const marginMatch = text.match(/Profit Margin:\s*([\d.]+)%/);
    if (marginMatch) sections.fundamentals.profit_margin = parseFloat(marginMatch[1]);
    
    const growthMatch = text.match(/Revenue Growth:\s*([\d.]+)%/);
    if (growthMatch) sections.fundamentals.revenue_growth = parseFloat(growthMatch[1]);
    
    // Parse social sentiment
    const redditMatch = text.match(/Reddit:\s*([A-Z\s]+)\s*\((\d+)% bullish,\s*(\d+) mentions\)/);
    if (redditMatch) {
      sections.sentiment_data.reddit = {
        sentiment_label: redditMatch[1].trim(),
        sentiment_score: parseInt(redditMatch[2]) / 100,
        mention_volume: parseInt(redditMatch[3])
      };
    }
    
    const twitterMatch = text.match(/Twitter:\s*([A-Z\s]+)\s*\((\d+)% bullish/);
    if (twitterMatch) {
      sections.sentiment_data.twitter = {
        sentiment_label: twitterMatch[1].trim(),
        sentiment_score: parseInt(twitterMatch[2]) / 100
      };
    }
    
    return { ...data, ...sections };
  }

  // Render charts if present
  if (msg.charts && msg.charts.length > 0) {
    console.log('📊 Rendering', msg.charts.length, 'chart(s)');
    msg.charts.forEach((chartData, idx) => {
      console.log(`Chart ${idx}:`, chartData.type, chartData.ticker);
      const chartContainer = window.chartManager.createChartContainer();
      row.appendChild(chartContainer);
      
      // Render chart after DOM insertion
      setTimeout(() => {
        try {
          if (chartData.type === 'comparison') {
            window.chartManager.renderComparisonChart(chartContainer.id, chartData);
          } else if (chartData.type === 'heatmap') {
            window.chartManager.renderSectorHeatmap(chartContainer.id, chartData);
          } else {
            window.chartManager.renderPriceChart(chartContainer.id, chartData);
          }
          console.log('✅ Chart rendered:', chartContainer.id);
        } catch (e) {
          console.error('❌ Chart render error:', e);
        }
      }, 100);
    });
  }

  chatEl.appendChild(row);
}

function renderTyping() {
  const row = document.createElement('div');
  row.className = 'row assistant';  // Match CSS expectations
  row.dataset.typing = '1';

  const bubble = document.createElement('div');
  bubble.className = 'bubble typing-bubble';
  
  // Create animated dots
  const wrap = document.createElement('div');
  wrap.className = 'typing';
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('span');
    dot.className = 'dot';
    wrap.appendChild(dot);
  }
  
  bubble.appendChild(wrap);
  row.appendChild(bubble);
  chatEl.appendChild(row);
  scrollToBottom();
  return row;
}

function clearTyping() {
  const node = chatEl.querySelector('[data-typing="1"]');
  if (node) node.remove();
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    chatEl.scrollTop = chatEl.scrollHeight + 9999;
  });
}

function bootstrapIfEmpty() {
  if (state.messages.length === 0) {
    addMessage('assistant',
      "Welcome to Orthogonal. Ask me about any stock for institutional-grade analysis.\n\nTry: 'Should I buy Tesla?' or 'Compare NVDA vs AMD'");
  } else {
    renderAll();
  }
}

function setSending(disabled) {
  inputEl.disabled = disabled;
  sendBtn.disabled = disabled;
}

async function onSend() {
  const text = inputEl.value.trim();
  if (!text) return;
  inputEl.value = '';
  resizeTextarea();

  addMessage('user', text);
  setSending(true);

  const typingNode = renderTyping();
  try {
    await sendToBackend(text);
    // Poll for assistant response
    await pollForAssistant(text, { attempts: 30, intervalMs: 1000 });
    clearTyping();
    // Sync UI with server history
    await syncHistory();
  } catch (err) {
    console.error(err);
    clearTyping();
    addMessage('assistant', "Error processing your request. Please try again or rephrase your question.");
  } finally {
    setSending(false);
  }
}

function resizeTextarea() {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(160, inputEl.scrollHeight) + 'px';
}

async function sendToBackend(text) {
  // Build conversation history from current messages
  const history = state.messages.map(m => ({
    role: m.role,
    content: m.text
  }));
  
  // Add the new user message
  history.push({ role: 'user', content: text });
  
  const res = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session: sessionId,
      messages: history,
    }),
  });
  if (!(res.ok || res.status === 202)) {
    const detail = await res.text();
    throw new Error(detail || `Request failed (${res.status})`);
  }
}

async function pollForAssistant(userText, { attempts = 20, intervalMs = 1000 } = {}) {
  for (let i = 0; i < attempts; i++) {
    await new Promise(r => setTimeout(r, intervalMs));
    const data = await fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { cache: 'no-store' }).then(r => r.json()).catch(() => null);
    if (!data || !Array.isArray(data.messages)) continue;
    const current = data.messages;
    const hasUser = current.some(m => m.role === 'user' && (m.content || m.text) === userText);
    const last = current[current.length - 1];
    const assistantReplied = hasUser && last && last.role === 'assistant';
    if (assistantReplied) return;
  }
}

async function syncHistory() {
  try {
    const data = await fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { cache: 'no-store' }).then(r => r.json());
    if (Array.isArray(data?.messages)) {
      // Map server shape to UI shape, preserving charts
      state.messages = data.messages.map((m, i) => ({ 
        id: m.id || `srv-${i}`, 
        role: m.role, 
        text: m.content || m.text, 
        t: m.timestamp || now(),
        charts: m.charts || []
      }));
      save();
      renderAll();
    }
  } catch (e) {
    console.error('syncHistory failed', e);
  }
}

function onReset() {
  fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { method: 'DELETE' })
    .catch(() => {})
    .finally(async () => {
      state.messages = [];
      save();
      renderAll();
      bootstrapIfEmpty();
    });
}

// Events
sendBtn.addEventListener('click', onSend);
resetBtn.addEventListener('click', onReset);
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    onSend();
  }
});
inputEl.addEventListener('input', resizeTextarea);

// Init
syncHistory().finally(() => {
  renderAll();
  bootstrapIfEmpty();
  resizeTextarea();
});

function getSessionId() {
  try {
    const existing = localStorage.getItem(SESSION_KEY);
    if (existing && existing.length > 0) return existing;
    const id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
    return id;
  } catch {
    // Fallback for very old browsers or blocked storage
    return 'default';
  }
}
