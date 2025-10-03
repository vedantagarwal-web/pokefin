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
  
  // Convert URLs to clickable links (styling handled by CSS)
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  const linked = escaped.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Convert newlines to <br>
  return linked.replace(/\n/g, '<br>');
}

function renderMessage(msg) {
  const row = document.createElement('div');
  row.className = `row ${msg.role === 'user' ? 'out' : 'in'}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = linkifyText(msg.text);
  row.appendChild(bubble);

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
  row.className = 'row in';
  row.dataset.typing = '1';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
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
      "Hey! I’m Pokefin. I keep things simple and actionable. What’s your first name and how comfortable do you feel with risk — cautious, balanced, or bold?");
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
    addMessage('assistant', "Oops, I hit a snag. Mind trying that again?");
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
